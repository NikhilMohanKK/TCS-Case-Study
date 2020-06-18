# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)
z=0
account=None
aid=None
cid=None
transamt=None
account=None
duser=None
user=None
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global z
    z=0
    return redirect('/')
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Fetch form data
        global z
        userDetails = request.form
        print(userDetails)
        Login_id = userDetails['Login_id']
        password = userDetails['password']
        cur = mysql.connection.cursor()
        resultValue = cur.execute("select Password from userstore where Login=%s",[Login_id])
        if resultValue > 0:
            userDetails = cur.fetchone()
        print(userDetails)
        cur.close()
        if z==0:
            if password in userDetails:
                z+=1
                print(z)
                return ('SUCCUSS')
                
            else:
                return ('ERROR')
        else:
            return ('session active')
       
    return render_template('01 Login Page.html')

@app.route('/createcustomer', methods=['GET', 'POST'])
def createcustomer():
    if request.method == 'POST':
        # Fetch form data
        userDetails = dict(request.form)
        print(userDetails)
        cur = mysql.connection.cursor()
        z=cur.execute("SELECT * FROM Customer WHERE ws_ssn= %s",(userDetails["ssn_id"],))
        print(z)
        if(len(userDetails["ssn_id"])==9 and z==0):
            
            cur.execute("insert into Customer(ws_ssn,ws_name,ws_age,ws_adrs) values (%s,%s,%s,%s)",(userDetails["ssn_id"],userDetails["name"],userDetails["age"],userDetails["addr"]))
            mysql.connection.commit()
            cur.execute("SELECT MAX(ws_cust_id) FROM Customer");
            cust_id = cur.fetchone()
            print(cust_id)
            cur.execute("insert into customerstatus(ws_ssn_id,ws_cust_id,Status,Message) values (%s,%s,%s,%s)",(userDetails["ssn_id"],cust_id,"Active","customer created succussfully"))
            mysql.connection.commit()
            cur.close()
            return('succuss')
        else:
            return('error')
        
    return render_template('02 Create Customer.html')
@app.route('/customersearch/<int:check>', methods=['GET', 'POST'])
def customersearchupdate(check):
    if request.method == 'POST':
        # Fetch form data
        global user
        global duser 
        userDetails = dict(request.form)
        print(userDetails)
        ssnid=userDetails['ssnid']
        custid=userDetails['custid']
        cur = mysql.connection.cursor()
        
        if(ssnid=='' and custid==''):
            return('error')
        if(ssnid!='' and custid!=''):
            z=cur.execute("SELECT * FROM Customer WHERE ws_ssn= %s AND ws_cust_id=%s",(userDetails["ssnid"],userDetails['custid']))
            

        if(ssnid!=''):
            z=cur.execute("SELECT * FROM Customer WHERE ws_ssn= %s ",(userDetails["ssnid"],))
           

        if(custid!=''):
            z=cur.execute("SELECT * FROM Customer WHERE  ws_cust_id=%s",(userDetails['custid'],))
       
        if check==1:
            if(z==0):
                return('NO CUSTOMER')
            else:
                user =cur.fetchone()
                print(user)
                return redirect('/updatecustomer')
        if check==2:
            if(z==0):
                return('NO CUSTOMER')
            else:
                duser =cur.fetchone()
                return redirect('/deletecustomer')
        #return redirect('/updatecustomer')
        cur.close() 
    return render_template('09 customer search.html')

@app.route('/updatecustomer', methods=['GET', 'POST'])
def updatecustomer():
    
    global user
    print(user)
    if request.method == 'POST':
        # Fetch form data
        userDetails = dict(request.form)
        print(userDetails)
        cur = mysql.connection.cursor()
        z=cur.execute("UPDATE Customer SET ws_name = %s, ws_adrs= %s,ws_age=%s WHERE ws_cust_id =%s",(userDetails['name'],userDetails['adr'],userDetails['age'],user[1]))
        mysql.connection.commit()
        cur.execute("UPDATE customerstatus set Status=%s,Message=%s,Last_Updates=CURRENT_TIMESTAMP where ws_cust_id =%s",("Active","customer update complete",user[1],))
        mysql.connection.commit()
        cur.close()
        return('succuss')
    return render_template('03 UpdateCustomer.html',ssnid=user[0],custid=user[1],name=user[2],adr=user[3],age=user[4])

@app.route('/deletecustomer', methods=['GET', 'POST'])
def deletecustomer():
    
    
    global duser
    print(duser)
    if request.method == 'POST':
        # Fetch form data
        userDetails = dict(request.form)
        print(userDetails)
        cur = mysql.connection.cursor()
        z=cur.execute("delete from Customer  WHERE  ws_cust_id=%s",(duser[1],))
        mysql.connection.commit()
        cur.execute("UPDATE customerstatus set Status=%s,Message=%s,Last_Updates=CURRENT_TIMESTAMP where ws_cust_id =%s",("Active","customer deleted successfully",duser[1]))
        mysql.connection.commit()
        cur.close()
        return('succuss')
    return render_template('04 Delete Customer.html',ssnid=duser[0],name=duser[2],adr=duser[3],age=duser[4])

@app.route('/customerstatus')
def customerstatus():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM customerstatus")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('05 Customer Status.html',userDetails=userDetails)

@app.route('/accountstatus')
def accountstatus():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM accountstatus")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('05 Customer Status.html',userDetails=userDetails)

@app.route('/createacct',methods = ['POST', 'GET'])
def createacctpage():
    if request.method == 'POST':
        userDetails = dict(request.form)
        print(userDetails)
        cur = mysql.connection.cursor()
        Customer_id= userDetails['custid']
        z=cur.execute("select * from customer where ws_cust_id=%s",[Customer_id])
        if z!=0:
            Actype = userDetails['acttype']
            if(Actype=='Current Account'):
                AccountType='c'
            elif(Actype=='Savings Account'):
                AccountType='s'
            #print(AccountType)
            DepAmount=userDetails['amount']
            cur = mysql.connection.cursor()
            
            z=cur.execute("select * from Account where ws_cust_id=%s and ws_acct_type=%s",(Customer_id,AccountType))
            if z==0:
                cur.execute("insert into Account (ws_cust_id,ws_acct_type,ws_acct_balance) values(%s,%s,%s)",(Customer_id,AccountType,DepAmount))
                mysql.connection.commit()
            else:
                return ("Account Exist")
            dataval=cur.execute("select * from Account where ws_cust_id=%s",[Customer_id])
            if dataval>0:
                print("MOER THAN WON")
                singledet=cur.fetchone()
                print(singledet[1])
                
                Message="Account Created Successfully"
                cur.execute("insert into AccountStatus (ws_cust_id,ws_acct_id,ws_acct_type,Status,Message) values(%s,%s,%s,%s,%s)",(Customer_id,singledet[1],AccountType,"Active",Message))
                mysql.connection.commit()
            cur.close()
            return "SUCCESS:"
        else:
            return "no customer"
        
    #return redirect(url_for('create_table'))"""
    return render_template('06 Create Account.html')
    

@app.route('/deleteacctpage',methods = ['POST', 'GET'])
def deleteacctpage():
    if request.method == 'POST':
        userDetails = request.form
        selecttype=userDetails['confirmtype']
        selectedact=int(userDetails['selectact'])
        if(selecttype=='Current'):
            selecttype='c'
        elif(selecttype=='Saving'):
            selecttype='s'
        global account
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
    print("HELLOWORLD")
    global account
    return render_template('07 Delete Account.html',actid=account)





@app.route('/accountsearch/<int:check>',methods=["GET","POST"])
def searchacc(check):
    if request.method == 'POST':
        userDetails = request.form
        acctid=None
        custid=None
        acctid=userDetails['actid']
        custid=str(userDetails['cstid'])
        global cid
        cid=custid
        global aid
        aid=acctid
        cur = mysql.connection.cursor()
        resultValue=cur.execute("select * from Account where ws_acct_id=%s OR ws_cust_id like %s",[acctid,custid])
        global account
        if resultValue>0:
            account=cur.fetchone()
            print(account)
            cid=account[0]
            aid=account[1]
            #return render_template('08 Account Status.html',userdet=dets)    
            ctr = mysql.connection.cursor()
            global customer
            resValue=ctr.execute("select * from Customer where ws_cust_id=%s",[account[0]])
            if resValue>0:
                customer=ctr.fetchone()
                print(customer)
            if check==1:
                #return render_template('07 Delete Account.html',userdet=dets)
                return redirect(url_for('deleteacctpage'))
            elif check==2:
                return redirect(url_for('confirmdep'))
            elif check==3:
                return redirect(url_for('confirmwit'))
            elif check==4:
                return redirect(url_for('confirmtrn'))
        else:
            return "Customer Doesnt Exist"
        #return render_template('08 Account Status.html',userdet=dets)    
    return render_template('10 Account Search.html')





@app.route('/depositmoney')
def deposit():
    chk=2
    return redirect(url_for('searchacc',check = chk))


@app.route('/depositafter',methods=["GET","POST"])
def confirmdep():
    global cid
    global aid
    global account
    if request.method == 'POST':
        userDetails = request.form
        acctid=int(userDetails['acct'])
        updamt=userDetails['depamt']
        cur = mysql.connection.cursor()
        cur.execute("update Account set ws_acct_balance = ws_acct_balance + %s where ws_acct_id=%s",[updamt,acctid])
        mysql.connection.commit()
        stringval="Deposited "+updamt+" from Account"
        global transamt
        transamt=updamt
        cur.execute("update AccountStatus set Message = %s where ws_acct_id=%s",[stringval,acctid])
        mysql.connection.commit()
        srctype='c'
        transtype='d'
        cur.execute("insert into transactions (ws_acct_id,ws_trxn_type,ws_amt,ws_src_act_type,ws_dest_act_type) values(%s,%s,%s,%s,%s)",(aid,transtype,transamt,srctype,account[2]))
        mysql.connection.commit()
        cid=None
        aid=None
        transamt=None
        account=None
        return "Deposited Successfully"
    return render_template('11 Deposit Amount.html',actid=account)
                
@app.route('/withdrawmoney')
def withdraw():
    chk=3
    return redirect(url_for('searchacc',check = chk))

@app.route('/withdrawafter',methods=["GET","POST"])
def confirmwit():
    global cid
    global aid
    global account
    if request.method == 'POST':
        userDetails = request.form
        acctid=int(userDetails['acct'])
        updamt=userDetails['depamt']
        cur = mysql.connection.cursor()
        z=cur.execute("select * from Account where ws_acct_id=%s and ws_acct_balance - %s >-1 ",[acctid,updamt])
        if z==0:
            return("insufficient balance")
        cur.execute("update Account set ws_acct_balance = ws_acct_balance - %s where ws_acct_id=%s",[updamt,acctid])
        mysql.connection.commit()
        stringval="Withdrawn "+updamt+" from Account"
        global transamt
        transamt=updamt
        cur.execute("update AccountStatus set Message = %s where ws_acct_id=%s",[stringval,acctid])
        mysql.connection.commit()
        srctype='c'
        transtype='w'
        cur.execute("insert into transactions (ws_acct_id,ws_trxn_type,ws_amt,ws_src_act_type,ws_dest_act_type  ) values(%s,%s,%s,%s,%s)",(aid,transtype,transamt,srctype,account[2]))
        mysql.connection.commit()
        cid=None
        aid=None
        transamt=None
        account=None
        return "Withdrawn Successfully"
    return render_template('12 Withdraw Amount.html',actid=account)

@app.route('/transfermoney')
def transfer():
    chk=4
    return redirect(url_for('searchacc',check = chk))

@app.route('/transferafter',methods=["GET","POST"])
def confirmtrn():
    global cid
    global aid
    global customer
    global account
    #print(customer)
    if request.method == 'POST':
        userDetails = request.form
        custid=int(userDetails['acctid'])
        custname=userDetails['actname']
        srctype=userDetails['srcact']
        dsttype=userDetails['dstact']
        if(srctype=='Current Account'):
            srctype='c'
            src='Current Account'
        elif(srctype=='Savings Account'):
            srctype='s'
            src='Savings Account'
        if(dsttype=='Current Account'):
            dsttype='c'
            dst='Current Account'
        elif(dsttype=='Savings Account'):
            dsttype='s'
            dst='Savings Account'
        print(srctype)
        tramt=userDetails['amt']
        cur = mysql.connection.cursor()
        stringval="Transferred "+tramt+"from "+src+" to "+dst
        global transamt
        transamt=tramt
        transtype='t'
        cur.execute("insert into transactions (ws_acct_id,ws_trxn_type,ws_amt,ws_src_act_type,ws_dest_act_type) values(%s,%s,%s,%s,%s)",(aid,transtype,tramt,srctype,dsttype))
        mysql.connection.commit()
        cid=None
        aid=None
        transamt=None
        customer=None
        return "Transferred Successfully"
    return render_template('13 Transfer Money.html',custid=customer)

@app.route('/accountstatementA',methods=["GET","POST"])
def accountstatementA():
    global aid
    if request.method == 'POST':
        userDetails = dict(request.form)
        print(userDetails)
        aid=userDetails["acctid"]
        if(userDetails["exampleRadios"]=="no"):
            cur = mysql.connection.cursor()
           
            n=int(userDetails["no"])
            z=cur.execute("select * from transactions where ws_acct_id=%s ORDER BY ws_rxn_date desc LIMIT %s",(aid,n))
            if z>0:
                res=cur.fetchall()
                
                return render_template('14a Acount Statement.html',userDetails=res)
            else:
                return("NO TRANSACTIONS YET")
            
        else:
            return redirect('/accountstatementB')
        cur.close()
    return render_template('14a Acount Statement.html')

@app.route('/accountstatementB',methods=["GET","POST"])
def accountstatementB():
    global aid
    if request.method == 'POST':
        userDetails =dict(request.form)
        print(userDetails)
        aid=userDetails["acctid"]
        
        cur = mysql.connection.cursor()
        start=userDetails["start"].split('/').reverse()
        start=('-').join(start)
        end=userDetails["end"].split('/').join('-').reverse()
        end=('-').join(end)
        z=cur.execute(" select * from transactions where ws_acct_id=%s and ws_rxn_date BETWEEN '%s 00:00:00' and '%s 23:59:59';",(aid,start,end))
        if z>0:
            res=cur.fetchall()
            
            return render_template('14a Acount Statement.html',userDetails=res)
        else:
            return("NO TRANSACTIONS YET")
            
       
        cur.close()
        
            
    return render_template('14b AccountStatement.html')


if __name__ == '__main__':
    app.run(debug=True)
