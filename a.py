import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import AgentExecutor, create_openai_functions_agent
from tools import save_tool, AquilaTool
from flask import Flask,render_template,redirect,url_for,request,jsonify
import random
import string
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from flask_cors import CORS
from langchain.memory import ConversationBufferWindowMemory

# Initialize memory with window of 6 exchanges
memory = ConversationBufferWindowMemory(k=6, return_messages=True, memory_key="chat_history")

lo=[]
# Load from cache (no more download)
app=Flask(__name__,template_folder='Templates')
CORS(app, origins="*")

def load_memory():
    if os.path.exists("chat_history.json"):
        try:
            with open("chat_history.json", "r", encoding="utf-8") as f:
                history = json.load(f)
            memory.clear()
            for msg in history:
                if msg['role'] == 'user':
                    memory.chat_memory.add_message(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    memory.chat_memory.add_message(AIMessage(content=msg['content']))
            print(f"Loaded {len(history)//2} conversation turns")
        except Exception as e:
            print(f"Error loading memory: {e}")
            memory.clear()

def save_memory():
    try:
        history = []
        for msg in memory.chat_memory.messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            history.append({"role": role, "content": msg.content})
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving memory: {e}")

load_memory()
email1=[]
email2=[]
import string
@app.route("/",methods=["POST","GET"])
def GPT():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            user=data.get('user1')
        else:
            # Handle form submission
            user = request.form.get("user1")
            email = request.form.get("email", "")
        class ResearchResponse(BaseModel):
                topic: str
                summary: str
                output: str
                sources: list[str]
                tools_used: list[str]
            # openai.api_key=token
        llm= ChatOpenAI(model="gpt-4o-mini",
        api_key=os.getenv('NEWAPI'),
        temperature=0.7
        )
        # llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        # parser = PydanticOutputParser(pydantic_object=ResearchResponse)
        # print(completion.choices[0].message)
        # messages=[
        #         SystemMessage(content="You are a helpful assistant."),
        #         HumanMessage(content=user)
        # ]
        parser = PydanticOutputParser(pydantic_object=ResearchResponse)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a research assistant that will help generate a research paper.  if the user greets, make sure to greet them in your output.
                    Answer according to Carfax-education's official website.
                    You must always use the provided tool to answer questions about Carfax-education website. If the tool returns no relevant data, say 'sorry, no relevant data found'.
                    bear in mind that , 
                    try to answer in 
                    a convincing way. if there is no relevant
                    data, just simply say 'sorry, no relevant data found'.
                    Wrap the output in this format and provide no other text\n{format_instructions},
                    """,
                
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{query}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        tools = [AquilaTool()]
        
        # Create an instance of the wrapper
        agent = create_tool_calling_agent(
            llm=llm,
            prompt=prompt,
            tools=tools
        )
        agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)
        query = str(user) + f"only search Carfax-education's official website"
        print(user)

        memory.chat_memory.add_message(HumanMessage(content=user))

        chat_history_msgs = memory.load_memory_variables({})["chat_history"]
        raw_response = agent_executor.invoke({
            "query": query,
            "chat_history": chat_history_msgs
        })
        print(raw_response['output'])
        structured_response = raw_response['output']
        print(structured_response)
    # except:
    #        return redirect(url_for("free"))
                    # return completion.choices[0].message.content

        memory.chat_memory.add_message(AIMessage(content=structured_response))
        save_memory()
    # j=str(structured_response).find("sources")
    # k=str(structured_response).find("summary")
    # v=str(structured_response).find("tools_used")
    # b=structured_response
    # Return proper JSON response for AJAX requests
    # if request.is_json:
        
        try:
                if 'no relevant data ' in str(structured_response):
                        return jsonify({"output": """you can contact:
                                        UK +44 20 7927 6207
Monaco +377 98 80 11 80
UAE  +971 4 438 5276
Hong Kong +852 5803 2742
Russia +7 (495) 775 42 60
Brazil +55 11 9 1468 0145"""})
                else:
                    f=str(structured_response).find('output')
                    v1=str(structured_response).find('summary')
                    f1=str(structured_response).find('sources')
                    # m=str(structured_response)[v:f].replace('summary','')
                    # nm=str(structured_response)[f:f1].replace('output','') 
                    # n=str(m).replace('output','')
                    # print(n)
                    # mb=n.replace(':','')
                    # b=str(nm)+str(m)
                    print(str(structured_response[v1+1:f1]))
                    print(structured_response)
                    return f'{structured_response[v1+1:f1]} , {render_template("fl1.html")}'
                    
        except:
                print(structured_response)
                
        
    
        # else:
                # Return HTML for form submissions
            
    
    # except Exception as e:
    #     if request.is_json:
    #         return f'{jsonify({"error": "Error parsing response", "details": str(e)}), 500}'
    #     else:
        #         return "Error parsing response", e, "Raw Response - ", raw_response
    return render_template("fl1.html")
# # example: access emails from Admissions page

# @app.route("/l")
# def ch():
#     return render_template("email.html")
# lo=[]
# lp=[]
# # @app.route("/oi")
# # def oi():
# li=random.choices(string.digits, k=6)
# @app.route("/code",methods=["POST","GET"])
# def code():
#     # lp=[]
#     # max_retries = 5
#     # base_wait_time = 2 
#     # # if request.method == "POST":
#     # if request.method == "POST":
#     #             code = request.form.get("code")
#                 # email=request.form.get("email")
#      # if email not in signed_in_users:
#      #     return redirect(url_for("sign_in"))
#      # else:
#                 # language = request.form.get("language of response")
#                 # user = request.form.get("user")
#                 # email2=request.form.get("email1")
#                 # email1=input("")
#                 import smtplib
#                 from email.message import EmailMessage
#                 l=[]
#                 # email2.append(email1[0])
#                                     #  return redirect(url_for("IsraelGPT"))
#                 # Configure your Outlook email credentials
#                 OUTLOOK_EMAIL = str(''.join(email1))# Replace with your Outlook email address
#                 OUTLOOK_PASSWORD = "zvju tgad kioo pspy"  # Replace with your password or App Password
#                 email = EmailMessage()
#                 email["from"] = "Mosh Khajavi"  # Replace with your name
#                 email["to"] = "arash.khajavi.ghk123@gmail.com" # Replace with the recipient's email address
#                 # print(str(email2))
#                 email["subject"] = "inquiry"
#                 # lu=random.randint(0,9)
#                 email.set_content(
#                     "there is an inquiry"
#                 )
#                 p = []
#                 # p.append(li)
#                 # Send the email using Outlook's SMTP server
#                 # e=str(email2)
#                 # lp.append(e)
#                 # for e in str(email2):
#                 #     p.append(e)
#                 # pr = "".join(p)
#                 # lp.append(str(pr))
#                 # print(lp)
#                 # try:
#                 k=[]
#                 with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
#                         smtp.ehlo()  # Identify yourself to the server
#                         smtp.starttls()  # Secure the connection
#                         smtp.login(OUTLOOK_EMAIL, OUTLOOK_PASSWORD)  # Log in to your Outlook account
#                         smtp.send_message(email)
                        
 
#                         # return str(email)
#                 #                 print(str(email).split("1.0")[1].strip())
#                 #                 if str(code) == str(str(email).split("1.0")[1].strip()):
#                 # #             lk.append(j1[0])
#                 # #             print(lk)
#                 # #
#                 # #
#                 # #
#                 # #             #  re=request.form.get("choice1")
#                 # #             #  if str(re) == "fast":
#                 # #                     j1.clear()
#                 # #                     return redirect(url_for("IsraelGPT"))
                
#                  #             lk.append(j1[0])
#                  #             print(lk)
#                  #             #  re=request.form.get("choice1")
#                  #             #  if str(re) == "fast":
#                  #                     k.append(j1[0])
#                  #                     j1.clear()
                                 
#                             #  elif str(re) == "slow":
#                             #   return redirect(url_for("chat"))
#                 # else:
#                 #             import time
#                 #             time.sleep(10)
#                             # li="".join(random.choices(str//
#                             # return redirect(url_for("oi"))
#                             # li=random.choices(string.digits,k=6)
#                             # return f"unsuccessful , {str(code)} , {str(li)}"
#                 # except:
#                 #     pass
# @app.route("/free",methods=['POST','GET'])
# def free():
#     if request.method == 'POST':
#       if request.is_json:
#         data = request.get_json()
#         user=data.get('user1')
#         import requests
#         m=[]
#         payload = {
#             "model": 'gemma3:1b',
#             "prompt": str(user),
#             "stream": True
#         }
#         with requests.post('http://localhost:11434/api/generate', json=payload, stream=True) as response:
#             response.raise_for_status()
#             print(response)
#             for line in response.iter_lines():
#                 if line:
#                     data = line.decode("utf-8")
#                     b=str(data).find('response')
#                     b1=str(data).find(str(',"done":false}'))
#                     n=str(data).find('"done":true,"done_reason"')
#                     # print(b)
#                     print(''.join(str(data[b+10:b1]))[:n].replace('""',''), end="", flush=True)
#             #         # return str(''.join(m))
#             # pri=m[:-1]
#             # print(m)
#             # m.remove(m[-1])
#             # if '\\n\\n' in pri:
#             #     pri.remove('\\n\\n')
#             #     pri1=str(''.join(pri)).replace('.donetruedone_reasonstopcontext[1052364107389173331544692729206166236881106107105436810722055293124236764521397675446916777112729206166301954679938210882912367892367514962589052911443331544691677532114491018732939563885920616623678710823682952131535453121333154469133365601752875004083724812711632957326690236764382243422367642230631579723676453291923676121952729981372486007405771456573155186162367642440383187500155053286338573226172367611082368295213421005990183712730531213331544698083891723682927291894573701010156591572449643445573496191923676464121389943424596531427881009123676121957355405532149842487573672236761108101839105319100464382305312110823682952139767544692112453121669179119775319745061346872236772107123677218961938563546758050633315446944562367878702574141127692367614554544692367618542367865457257414112769236761455454469236761854310041072368295213114317477018114153121159974036623331544695602250943239104456653515415482367878702574141127692367614554544692367618542367865457257414112769236761455454469236761854310041081018711227918531212855360355732061667409729879268418832367613331544694038236789236745284763699106236764834625236789236751246217915316618607614156465285067798195952367611081018835125312180823677710066141249825380961053271149663695707236761117419385635732870465453283371861611862367645321677711233106369910623676110305635250531661860749615973636977105739106138998223530537196031082021160178625836119193644319382367641451611344278623678710823682913910181093665961156285683255653289120625101811747951601786158677985405236761]total_duration21007220600load_duration191567600prompt_eval_count15prompt_eval_duration220578700eval_count352eval_duration20593710700','')
#             #     return jsonify({
#             #             'output': f'{''.join(pri1)}'
#             #         })
#         print()
#     return render_template('button.html')
if __name__ == '__main__':
    app.run(debug=True)
