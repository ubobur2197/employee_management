from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)

    employees = db.relationship('Employee', back_populates='department')

    def __repr__(self):
        return f"<Department {self.nom}>"


class Employee(db.Model):
    __tablename__ = 'employees' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)

    department = db.relationship('Department', back_populates='employees')

    def __repr__(self):
        return f"<Employee {self.name} {self.last_name}>"
