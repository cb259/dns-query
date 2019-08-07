from flask import Flask, flash, redirect, render_template, request, session, abort
import dns.resolver

app = Flask(__name__)

@app.route('/',methods = ['POST', 'GET'])
def dnsQuery():
    if request.method == 'GET':
        # Render the main page
        return render_template('dns-query.html')
    elif request.method == 'POST':
        # Arguments to send to method
        hostname = str(request.form.get('hostname'))
        #name_server = str(request.form.get('name_server'))
        record_type = str(request.form.get('record_type'))

        # Build the results
        result = resolver(hostname,record_type)

        # Render the page with the results
        return render_template('dns-query.html',result=result)

def resolver(host, recordType):
    # Check if host is empty
    if host == "":
        return "No host provided!"

    # Check recordType value
    if recordType == "A":
        recordType = str("A")
    elif recordType == "ANY":
        recordType = str("")
    elif recordType == "CNAME":
        recordType = str("CNAME")
    elif recordType == "MX":
        recordType = str("MX")
    elif recordType == "NS":
        recordType = str("NS")
    elif recordType == "SOA":
        recordType = str("SOA")
    elif recordType == "SRV":
        recordType = str("SRV")
    elif recordType == "TXT":
        recordType = str("TXT")
    else:
        recordType = str("")

    # Run command and store results
    if recordType == "":
        try:
            query_result = dns.resolver.query(host)
        except dns.resolver.NXDOMAIN:
            return "ERROR: [NXDOMAIN] Unable to resolve domain as it does not exist."
        except:
            return "ERROR: [UNKNOWN] Unable to resolve the domain."
    else:
        try:
            query_result = dns.resolver.query(host, recordType)
        except dns.resolver.NXDOMAIN:
            return "ERROR: [NXDOMAIN] Unable to resolve domain/record combination as it does not exist."
        except:
            return "ERROR: [UNKNOWN] Unable to resolve the domain/record combination."

    # Return the command results
    return query_result.response

if __name__ == '__main__':
    app.run(debug = True)