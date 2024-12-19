# EZ


clone the repo, redirect to project folder(the cloned folder) and run with command uvicorn backend.main:app --port 8090 --reload 

initial step -------> Uvicorn running on http://127.0.0.1:8090  click on the link and Uvicorn running on http://127.0.0.1:8090/docs do this on browser move to the swagger and we are good to go

secondary step -----> you will have a env.txt file create a .env file and copy paste the env.txt content to the .env file


Step 1 create a venv for the python3 with command python3 -m venv venv and activate with the command source venv/bin/activate also please ensure that the interpreter is on venv only

step 2 install all the requirements with command pip install -r requirement.dev.txt

step 3 Now the shared .env file should be saved in the folder where requirement.txt is 

step 4 Now if you are using the same .env files you can just proceed with the signup(role can anything but if want to access the db use Ops)----->signupVerification--------> login-------> login verification--------> upload and all

step 5 Now if you are using same .env you can face some issue with db interaction. still try with 

setp 6 use your own .env file to further proceed if you decide to use custom .env plase after introducing the .env to code close the terminal after deactivating the venv and then again open the terminal and activate the venv

step 7 if using custom .env plese hit the dbchecker api to create the tables in your aws

step 8 please refrain to make unnecessary data on aws

step 9 flow will be like signup----> get a token----> hit signup verification introduce token to api and hit execute------> login ------> get a otp------> run for login verification

step 10 db willbe like upload data ---------> list all data-----------> get the preassigned data

Quesion1--->How do you plan on deploying this to the production environment?


Answer ---> i plan on deploying the code to lambda and minimize the layers used to get cost efficient server use gmail smtp for better result i have attached a test smtp file you can test it from there
the mail concept.