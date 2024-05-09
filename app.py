from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
import configparser

app = Flask(__name__)
Bootstrap(app)

config = configparser.ConfigParser()
config.read('config/database.ini')
secret_key = config['flask']['SECRET_KEY']  # 시크릿 키를 가져옴
db_user = config['postgresql']['user']
db_password = config['postgresql']['password']
db_host = config['postgresql']['host']
db_port = config['postgresql']['port']
db_name = config['postgresql']['database']

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key

db = SQLAlchemy(app)
migrate = Migrate(app,db)
CORS(app) # CORS 설정

# 인덱스 페이지
@app.route('/')
def index():
    seat_info=seats()   # 좌석 정보를 가져옴
    response = make_response(render_template('index.html', seats=seat_info))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'   # 캐시를 사용하지 않도록 설정
    response.headers['Pragma'] = 'no-cache'     # HTTP 1.0 캐시 방지
    response.headers['Expires'] = '0'   # 과거 날짜로 설정하여 캐시 만료시킴
    return response     # 인덱스 페이지를 반환

# 체크인 페이지
@app.route('/checkin')
def checkin():
    return render_template('checkin.html')

# 체크아웃 페이지
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

#? 학생 정보 임의 페이지
@app.route('/student_info')
def student_info():
    return render_template('student_info.html')

# 학생 정보를 등록하는 페이지
@app.route('/add_student', methods=['GET'])
def add_student():
    try:
        # 현재 할당되어있는 좌석
        occupied_seats = [student.seatnumber for student in db.session.query(Students.seatnumber).all()]
        # 모든 좌석 개수
        all_seats = set(range(1, 35))
        # 할당 가능한 좌석
        available_seats = list(all_seats - set(occupied_seats))
        if not available_seats: # 리스트가 비어있으면
            flash("할당 가능한 좌석이 없습니다.", category="warning")   # 경고 메시지 출력
            return redirect(url_for('index'))
        return render_template('add_student.html', available_seats=available_seats)
    except Exception as e: 
        flash(f"오류발생: {str(e)}", category="error")  # 에러 메시지 출력
        return redirect(url_for('index'))
    

'''
*********************
여기서부터는 api 코드
*********************
'''
#! 입실 처리를 하는 api 함수 (미완성)
@app.route('/api/checkin', methods=['POST'])
def api_checkin():
    return redirect(url_for('index'))

#! 퇴실 처리를 하는 api 함수 (미완성)
@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    return redirect(url_for('index'))

# 학생 아이디로부터 학생 정보를 가져오는 api함수
@app.route('/api/students/<int:studentid>', methods=['GET'])
def api_get_student(studentid):
    try:
        with Session() as session:
            student = session.get(Students, studentid)  # 데이터베이스 세션에서 학생 아이디로 정보를 가져옴
            if not student:
                return jsonify({'error': 'Student not found'}), 404
            student_data= {
                'student_id': student.studentid,
                'name': student.name,
                'phone_number': student.phonenumber,
                'seat_number': student.seatnumber
            }
            return jsonify(student_data)
    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500
    
# 좌석번호로부터 학생 정보를 가져오는 api 함수
@app.route('/api/students/<int:seatnumber>', methods=['GET'])
def api_get_student_from_seat(seatnumber):
    try:
        # 컨텍스트 매니저를 사용하여 데이터베이스 관련 세션을 시작
        with Session() as session:
            student = session.get(Students, seatnumber)  # 데이터베이스 세션에서 학생 좌석번호로 정보를 가져옴
            if not student:
                return jsonify({'error': 'Student not found'}), 404
            # 컨텍스트 내에서 모든 데이터를 로드하면 세션은 자동으로 닫힘
            student_data = {
                'student_id': student.studentid,
                'name': student.name,
                'phone_number': student.phonenumber,
                'seat_number': student.seatnumber
            }
            # 세션 외부에서 데이터 반환
            return jsonify(student_data)
    except Exception as e:
        # 에러 발생 시에 세션은 여전히 컨텍스트 관리자에 의해 닫힌다
        return jsonify({'error': 'Server error', 'message': str(e)}), 500

# 학생을 등록하는 api 함수
@app.route('/api/api_add_students', methods=['POST'])
def api_add_student():
    try:
        data = request.get_json()
        new_student = Students(
            name=data['name'],
            phonenumber = data['phonenumber'],
            seatnumber = data['seatnumber']
            )
        db.session.add(new_student)
        db.session.commit()
        
        return jsonify({'message': 'Student added successfully!'}), 201     # 201: Created
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Server error', 'message': str(e)}), 500




'''
*********************
여기서부터는 데이터베이스 모델 코드
*********************
'''

# 학생 정보를 저장하는 데이터베이스 모델
class Students(db.Model):
    __tablename__ = 'students'
    studentid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phonenumber = db.Column(db.String(20), nullable=False)
    seatnumber = db.Column(db.Integer, nullable=False, unique=True)

    # entryRecord와 관계 설정
    entry_records = db.relationship('EntryRecord', backref='students', lazy=True)

# 입실 기록을 저장하는 데이터베이스 모델
class EntryRecord(db.Model):
    __tablename__ = 'entryrecords'
    recordid = db.Column(db.Integer, primary_key=True)
    studentid = db.Column(db.Integer, db.ForeignKey('students.studentid'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    eventtype = db.Column(db.String(50), nullable=False)


'''
*********************
일반 flask 함수
*********************
'''
# 데이터베이스 세션을 종료하는 함수
@app.teardown_appcontext
def remove_session(*args, **kwargs):
    db.session.remove() # 데이터베이스 세션을 닫음


def seats():
    try:
        with Session() as session:
            students = Students.query.order_by(Students.seatnumber).all()
            seats_dict={student.seatnumber: student.name for student in students}
            return seats_dict
    except Exception as e:
        print("seats() error: " + e)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)