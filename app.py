from flask import Flask, redirect, render_template, request, flash, url_for
from models import db, Employee, Department
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///company.db'
app.secret_key = 'supersecretkey'
db.init_app(app)


def check(name):
    pattern = r"^[A-Za-zА-Яа-я]+$"
    if re.match(pattern, name):
        return True, f"'{name}' to'g'ri formatda."
    else:
        return False, f"'{name}' da noto'g'ri belgilar mavjud."


@app.route('/')
def index():
    title = "Bosh Sahifa"
    employees = Employee.query.order_by(Employee.salary.desc()).all()
    return render_template("index.html", title=title, employees=employees)


@app.route('/employee/add/', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        first_name = request.form['name'].title().strip()
        last_name = request.form['last_name'].title().strip()
        position = request.form['position'].title().strip()
        department_id = request.form['department_id'].strip()
        salary = request.form['salary'].strip()

        f_name = check(first_name)
        l_name = check(last_name)

        if not (f_name[0] and l_name[0]):
            if not f_name[0]:
                flash(f_name[1], 'warning')
            if not l_name[0]:
                flash(l_name[1], 'warning')
            return render_template('employee_add.html', departments=Department.query.all())

        missing = []
        if not first_name:
            missing.append("Ism")
        if not last_name:
            missing.append("Familiya")
        if not position:
            missing.append("Lavozim")
        if not department_id:
            missing.append("Bo'lim")

        if missing:
            flash(f"Quyidagi maydon(lar) bo'sh bo'lmasligi kerak: {', '.join(missing)}.", 'warning')
            return render_template('employee_add.html', departments=Department.query.all())

        if len(first_name) < 3 or len(last_name) < 3:
            flash("Ism va familiya kamida 3 ta belgidan iborat bo'lishi kerak.", 'warning')
            return render_template('employee_add.html', departments=Department.query.all())

        if len(first_name) > 50 or len(last_name) > 50:
            flash("Ism va familiya 50 ta belgidan oshmasligi kerak.", 'warning')
            return render_template('employee_add.html', departments=Department.query.all())

        salary_value = None
        if salary:
            try:
                salary_value = float(salary)
            except ValueError:
                flash("Maosh raqamli qiymat bo'lishi kerak.", 'warning')
                return render_template('employee_add.html', departments=Department.query.all())

        try:
            employee = Employee(
                name=first_name,
                last_name=last_name,
                position=position,
                department_id=department_id,
                salary=salary_value
            )
            db.session.add(employee)
            db.session.commit()
            flash("Xodim muvaffaqiyatli qo'shildi!", 'success')
            return redirect('/')
        except IntegrityError:
            db.session.rollback()
            flash("Xodim qo'shishda xato yuz berdi.", 'danger')
            return render_template('employee_add.html', departments=Department.query.all())

    departments = Department.query.all()
    return render_template('employee_add.html', departments=departments)


@app.route('/employee/update/<int:id>', methods=['GET', 'POST'])
def update_employee(id):
    employee = Employee.query.get_or_404(id)

    if request.method == 'POST':
        first_name = request.form['name'].strip().title()
        last_name = request.form['last_name'].strip().title()
        position = request.form['position'].strip().title()
        department_id = request.form['department_id'].strip()
        salary = request.form['salary'].strip()

        missing = []
        if not first_name:
            missing.append("Ism")
        if not last_name:
            missing.append("Familiya")
        if not position:
            missing.append("Lavozim")
        if not department_id:
            missing.append("Bo'lim")

        if missing:
            flash(f"Quyidagi maydon(lar) bo'sh bo'lmasligi kerak: {', '.join(missing)}.", 'warning')
            return render_template('employee_update.html', employee=employee, departments=Department.query.all())

        f_name = check(first_name)
        l_name = check(last_name)

        if not f_name[0]:
            flash(f_name[1], 'warning')
            return render_template('employee_update.html', employee=employee, departments=Department.query.all())

        if not l_name[0]:
            flash(l_name[1], 'warning')
            return render_template('employee_update.html', employee=employee, departments=Department.query.all())

        if len(first_name) < 3 or len(last_name) < 3:
            flash("Ism va familiya kamida 3 ta belgidan iborat bo'lishi kerak.", 'warning')
            return render_template('employee_update.html', employee=employee, departments=Department.query.all())

        if len(first_name) > 50 or len(last_name) > 50:
            flash("Ism va familiya 50 ta belgidan oshmasligi kerak.", 'warning')
            return render_template('employee_update.html', employee=employee, departments=Department.query.all())

        salary_value = None
        if salary:
            try:
                salary_value = float(salary)
            except ValueError:
                flash("Maosh raqamli qiymat bo'lishi kerak.", 'warning')
                return render_template('employee_update.html', employee=employee, departments=Department.query.all())

        try:
            employee.name = first_name
            employee.last_name = last_name
            employee.position = position
            employee.department_id = department_id
            employee.salary = salary_value

            db.session.commit()
            flash("Xodim ma'lumotlari muvaffaqiyatli yangilandi!", 'success')
            return redirect(url_for("index"))
        except IntegrityError:
            db.session.rollback()
            flash("Xodim ma'lumotlarini yangilashda xato yuz berdi.", 'error')
            return render_template('employee_update.html', employee=employee, departments=Department.query.all())

    departments = Department.query.all()
    return render_template('employee_update.html', employee=employee, departments=departments)


@app.route('/employee/delete/<int:id>', methods=['GET'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    try:
        db.session.delete(employee)
        db.session.commit()
        flash("Xodim muvaffaqiyatli o'chirildi!", 'success')
    except IntegrityError:
        db.session.rollback()
        flash("Xodimni o'chirishda xato yuz berdi.", 'danger')
    return redirect(url_for('index'))


@app.route('/employee/<int:id>', methods=['GET'])
def employee_detail(id):
    employee = Employee.query.get_or_404(id)
    return render_template('employee_detail.html', employee=employee)


@app.route('/employees/', methods=['GET'])
def employees():
    employees = Employee.query.order_by(Employee.salary.desc()).all()
    return render_template('employees.html', employees=employees)


@app.route('/department/<string:title>')
def department_employees(title):
    department = Department.query.filter_by(title=title).first_or_404()
    employees = Employee.query.filter_by(department_id=department.id).all()
    return render_template('department_employees.html', department=department, employees=employees)


@app.route('/department/add/', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        nom = request.form['nom'].title().strip()
        if not nom:
            flash("Bo'lim nomi bo'sh bo'lmasligi kerak.", 'warning')
            return render_template('department_add.html')
        try:
            department = Department(nom=nom)
            db.session.add(department)
            db.session.commit()
            flash("Bo'lim muvaffaqiyatli qo'shildi!", 'success')
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash("Bu nomdagi bo'lim allaqachon mavjud.", 'danger')
            return render_template('department_add.html')
    return render_template('department_add.html')


@app.route('/employees/salary-report')
def salary_report():
    avg_salary = db.session.query(func.avg(Employee.salary)).scalar()
    employees = Employee.query.order_by(Employee.salary.desc()).all()
    return render_template('salary_report.html', avg_salary=avg_salary, employees=employees)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)