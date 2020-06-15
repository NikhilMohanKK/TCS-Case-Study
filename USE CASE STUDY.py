# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 22:30:43 2020

@author: Nikhil Mohan K K
"""


from flask import Flask, render_template, request,redirect, url_for
from flask_mysqldb import MySQL
import yaml
app=Flask(__name__)
    

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']



mysql = MySQL(app)


@app.route('/login',methods = ['POST', 'GET'])
def loginpage():
    if request.method == 'POST':
        userDetails = request.form
        print(userDetails)
        Login_id = userDetails['username']
        password = userDetails['password']
        cur = mysql.connection.cursor()
        resultValue = cur.execute("select password from userstore where loginname=%s",[Login_id])
        if resultValue > 0:
            print("this also works")
            userDetails = cur.fetchone()
        print(userDetails)
        cur.close()
        if password in userDetails:
            return ('SUCCUSS')
        else:
            return ('ERROR')
    #return redirect(url_for('create_table'))
    return render_template('01 Login Page.html')


@app.route('/createacct',methods = ['POST', 'GET'])
def createacctpage():
    if request.method == 'POST':
        userDetails = request.form
        #print(userDetails)
        Customer_id= userDetails['custid']
        
        Actype = userDetails['acttype']
        if(Actype=='Current Account'):
            AccountType='c'
        elif(Actype=='Savings Account'):
            AccountType='s'
        #print(AccountType)
        DepAmount=userDetails['amount']
        cur = mysql.connection.cursor()
        crr = mysql.connection.cursor()
        cur.execute("insert into Account (ws_cust_id,ws_acct_type,ws_acct_balance) values(%s,%s,%s)",(Customer_id,AccountType,DepAmount))
        mysql.connection.commit()
        dataval=crr.execute("select * from Account where ws_cust_id=%s",[Customer_id])
        if dataval>0:
            print("MOER THAN WON")
            singledet=crr.fetchone()
            print(singledet[1])
            Status="Active"
            Message="Account Created Successfully"
            cur.execute("insert into AccountStatus (ws_cust_id,ws_acct_id,ws_acct_type,Status,Message) values(%s,%s,%s,%s,%s)",(Customer_id,singledet[1],AccountType,Status,Message))
            mysql.connection.commit()
        cur.close()
        return "SUCCESS:"
        
    #return redirect(url_for('create_table'))"""
    return render_template('06 Create Account.html')
    

@app.route('/deleteaccount',methods = ['POST', 'GET'])
def deleteacctpage():
    if request.method == 'POST':
        userDetails = request.form
        selecttype=userDetails['confirmtype']
        selectedact=int(userDetails['selectact'])
        if(selecttype=='Current Account'):
            selecttype='c'
        elif(selecttype=='Savings Account'):
            selecttype='s'
        print(type(selectedact))
        print(selectedact)
        print(selecttype)
        cur = mysql.connection.cursor()
        resultValue=cur.execute("select * from Account where ws_acct_id=%s",[selectedact])
        if resultValue > 0:
            userDetails = cur.fetchone()
            if selecttype in userDetails:   
                newstatus="Inactive"
                Message="Account Deleted Successfully"
                cur.execute("Delete from Account where ws_acct_id=%s and ws_acct_type=%s",[selectedact,selecttype])
                mysql.connection.commit()
                cur.execute("update AccountStatus set Status=%s,Message=%s where ws_acct_id=%s and ws_acct_type=%s",[newstatus,Message,selectedact,selecttype])
                mysql.connection.commit()
                return "Deleted:"
        else:
            return "No such Account"
        cur.close()
"""    res=cpl.execute("select ws_acct_id from Account")
    if(res>0):
        dets=cpl.fetchall()
        print(dets)
    cpl.close()
    return render_template('07 Delete Account.html',userdet=dets)
"""
    #return redirect(url_for('create_table'))"""
    

@app.route('/')
def hello():
    chk=1
    return redirect(url_for('searchacc',check = chk))

@app.route('/world')
def world():
    chk=2
    return redirect(url_for('searchacc',check = chk))



@app.route('/accountsearch',methods=["GET","POST"])
def searchacc():
    if request.method == 'POST':
        userDetails = request.form
        acctid=userDetails['actid']
        custid=userDetails['cstid']
        cur = mysql.connection.cursor()
        resultValue=cur.execute("select * from Account where ws_acct_id=%s or ws_cust_id=%s",[acctid,custid])
        if resultValue>0:
            dets=cur.fetchone()
            #return render_template('08 Account Status.html',userdet=dets)    
            return render_template('07 Delete Account.html',userdet=dets)
        else:
            return "Customer Doesnt Exist"
        #return render_template('08 Account Status.html',userdet=dets)    
    return render_template('10 Account Search.html')





@app.route('/depositmoney',methods=["GET","POST"])
def deposit():
    return render_template('11 Deposit Money.html')


@app.route('/')
def deletetry():
    value=3
    type='c'
    cur = mysql.connection.cursor()
    cur.execute("Delete from Account where ws_acct_id=%s and ws_acct_type=%s",[value,type])
    mysql.connection.commit()
                



if __name__=='__main__':
    app.debug=True
    app.run(host='127.0.0.1',port=5050,debug=False)
    