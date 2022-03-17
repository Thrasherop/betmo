"""
    Endpoints for betmo API. These endpoints start with /betmo/

    this app allows Megan and Josh to make bets on the number of
    cars at work each day. They each send a query containing their
    guess. At the end of the day, Megan will upload the final score.

    When the final score is submitted, the person with the closest guess
    will win the bet. The winners txt file will be updated with the new info

    The text files are stored in the /betmo/data directory. The name is "[user]_data.txt".
    The files are formatted as: `[current_balance]!!![total_guessed]`

    There is also the option to transfer balance via the /betmo/transfer_balance endpoint.

    TODO:
        -X Add a way to submit guesses
        -X Add a way to submit final socre
        -X Add a way to get current guesses
        -X Add a way to get current balance
        -X Add a way to get total wins
        - Add a way to transfer balance
"""

@app.route('/betmo/submit_guess', methods=['POST', 'GET'])
def betmo_submit_guess():
    """
    Endpoint for submitting guesses.

    Data is expected in the post in this format: `{User:[user], Guess:[guess]}`, 
    and that will be transformed into a dictionary as well as {Date:[date], Guess_Time:[time of submision]}

    Once finished, it will return a dictionary with the following format:
        {status: [status], message: [message]}


    """


    # Extract the post body from the request as a dictionary
    data = request.get_json()


    # Basic data validation
    if data['User'] is None:
        return jsonify({'status': 'error', 'message': 'User not found'})
    if data['Guess'] is None:
        return jsonify({'status': 'error', 'message': 'Guess not found'})


    try:
        
        # Loads the current guess file if it exists. If not, it creates a new one
        #if os.path.exists(CURRENT_GUESSES_FILE):
        try:
            with open(CURRENT_GUESSES_FILE, 'r') as f:
                current_guesses_raw = f.read()
                current_guesses = json.loads(current_guesses_raw)
        except:

            # Creates the paths
            dir_path = DATA_STORAGE_PATH.split("/")
            prev_dir = ""
            for dir in dir_path:
                
                prev_dir +=  dir + "/"

                if not os.path.exists(prev_dir):
                    os.makedirs(prev_dir)

                
            # Initializes the map
            current_guesses = {}

    except:
        return jsonify({'status': '500', 'message': 'Could not load (or initialize) current guesses'})


    try: 
        # Gets the guess
        current_guesses[data['User']] = {'Guess':data['Guess'], 'Guess_Time':dt.now().strftime("%Y-%m-%d %H:%M:%S")}
        
            
        # Writes the new guesses to the file
        with open(CURRENT_GUESSES_FILE, 'w+') as f:
            f.write(json.dumps(current_guesses))
            print("Updated the Guess")

    except:
        return jsonify({'status': '500', 'message': 'Could not write to current guesses file'})

    return jsonify({'status': '200', 'message': 'Guess submitted'})


@app.route('/betmo/submit_final_score', methods=['POST', 'GET'])
def betmo_submit_final_score():

    """
        Endpoint for Megan to submit her final score.


        Data is expected in the post in this format: `{'final_score':[final_score]}`.

        The contents of the winning user's data files will be updated with the new balance and count.
    """

    # Extract the post body from the request as a dictionary
    data = request.get_json()


    # Basic data validation
    if data['final_score'] is None:
        print("final score is none")
        return jsonify({'status': '400', 'message': 'Final score not found'})

    # Loads the current guess file if it exists. If not, it returns error 500
    try:
        with open(CURRENT_GUESSES_FILE, 'r') as f:
            current_guesses_raw = f.read()
            current_guesses = json.loads(current_guesses_raw)

    except Exception as e:
        print("Loading current guesses failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not load current guesses'})



    # Determines the winning user
    try:
        megan_guess = current_guesses[MEGAN_NAME]['Guess']
        josh_guess = current_guesses[JOSH_NAME]['Guess']

        megan_dx = abs(megan_guess - data['final_score'])
        josh_dx = abs(josh_guess - data['final_score'])

        if megan_dx < josh_dx:
            winning_user = MEGAN_NAME

        else:
            winning_user = JOSH_NAME

    except Exception as e:
        print("Determining winner failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not determine winning user: ' + str(e)})


    # Updates the winning user's cur balance file
    try:

        # Reads the current balance
        with open(DATA_STORAGE_PATH + winning_user + CURRENT_BALANCE_FILE_EXTENSION , 'r') as f:
            data_raw = f.read()
            data_dict = json.loads(data_raw)

        # Updates the balance

        #print(type(data_dict['balance']))
        new_balance = int(data_dict['balance']) + 1

        with open(DATA_STORAGE_PATH + winning_user + CURRENT_BALANCE_FILE_EXTENSION , 'w+') as f:
            f.write(json.dumps({'balance': new_balance}))


    except Exception as e:
        print("Updating winners balance failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not update winner\'s balance'})


    # Updates the winning user's guessed count
    try:

        # Reads the current balance
        with open(DATA_STORAGE_PATH + winning_user + TOTAL_WINS_FILE_EXTENSION , 'r') as f:
            data_raw = f.read()
            data_dict = json.loads(data_raw)

        # Updates the balance
        new_guessed = int(data_dict['total_wins']) + 1

        with open(DATA_STORAGE_PATH + winning_user + TOTAL_WINS_FILE_EXTENSION , 'w+') as f:
            f.write(json.dumps({'total_wins': new_guessed}))

    except Exception as e:
        print("Updating winners total failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not update winner\'s guessed count'})


    return jsonify({'status': '200', 'message': 'Final score submitted and balances updated'})


@app.route('/betmo/get_current_guesses', methods=['POST', 'GET'])
def betmo_get_current_guesses():

    """
        Endpoint to fetch all current guesses.
    
    """

    # Loads the current guesses
    try:
        with open(CURRENT_GUESSES_FILE , 'r') as f:
            guesses_raw = f.read()
            guesses = json.loads(guesses_raw)

    except Exception as e:
        print("Loading current guesses failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not load current guesses'})

    # Validates the guesses 
    try:
        if guesses is None:
            return jsonify({'status': '400', 'message': 'No guesses found'})

    except Exception as e:
        print("Validating guesses failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not validate guesses'})


    return jsonify({'status': '200', 'message': 'Current guesses retrieved', 'guesses': guesses})


@app.route("/betmo/get_balances", methods=['POST', 'GET'])
def betmo_get_balances():

    """
        Endpoint to fetch the current balances of all users.
    """

    # Loads the current balances
    try:
        with open(DATA_STORAGE_PATH + MEGAN_NAME + CURRENT_BALANCE_FILE_EXTENSION , 'r') as f:
            megan_balance_raw = f.read()
            megan_balance = json.loads(megan_balance_raw)

        with open(DATA_STORAGE_PATH + JOSH_NAME + CURRENT_BALANCE_FILE_EXTENSION , 'r') as f:
            josh_balance_raw = f.read()
            josh_balance = json.loads(josh_balance_raw)

    except Exception as e:
        print("Loading current balances failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not load current balances'})

    # Validates the balances
    try:

        if megan_balance is None:
            return jsonify({'status': '400', 'message': 'No Megan balances found'})

        if josh_balance is None:
            return jsonify({'status': '400', 'message': 'No Josh balances found'})

    except Exception as e:
        print("Validating balances failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not validate balances'})

    return jsonify({'status': '200', 'message': 'Current balances retrieved', 'balances': {MEGAN_NAME: megan_balance, JOSH_NAME: josh_balance}})


@app.route("/betmo/get_total_wins", methods=['POST', 'GET'])
def betmo_get_total_wins():

    """
        Endpoint to fetch the total wins of all users.
    """

    # Loads the current balances
    try:
        with open(DATA_STORAGE_PATH + MEGAN_NAME + TOTAL_WINS_FILE_EXTENSION , 'r') as f:
            megan_total_raw = f.read()
            megan_total = json.loads(megan_total_raw)

        with open(DATA_STORAGE_PATH + JOSH_NAME + TOTAL_WINS_FILE_EXTENSION , 'r') as f:
            josh_total_raw = f.read()
            josh_total = json.loads(josh_total_raw)

    except Exception as e:
        print("Loading current balances failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not load current balances'})

    # Validates the balances
    try:

        if megan_total is None:
            return jsonify({'status': '400', 'message': 'No Megan total wins found'})

        if josh_total is None:
            return jsonify({'status': '400', 'message': 'No Josh total wins found'})

    except Exception as e:
        print("Validating balances failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not validate balances'})

    return jsonify({'status': '200', 'message': 'Current total wins retrieved', 'total_wins': {MEGAN_NAME: megan_total, JOSH_NAME: josh_total}})


@app.route("/betmo/transfer_balance", methods=['POST', 'GET'])
def betmo_transfer_balance():

    """
        Transfers balance from one user to another.

        Data comes in formated as this: {'from': 'user_name', 'to': 'user_name', 'amount': 'amount'}.

    """

    # Extracts the data from the request
    try:
        data_raw = request.get_data()
        data = json.loads(data_raw)

    except Exception as e:
        print("Extracting data failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not extract POST request'})


    # Loads the current balances
    try:
        # Initializes the balance map
        balances = {MEGAN_NAME: {}, JOSH_NAME: {}}

        with open(DATA_STORAGE_PATH + MEGAN_NAME + CURRENT_BALANCE_FILE_EXTENSION , 'r') as f:
            megan_balance_raw = f.read()
            #megan_balance = json.loads(megan_balance_raw)
            balances[MEGAN_NAME] = json.loads(megan_balance_raw)

        with open(DATA_STORAGE_PATH + JOSH_NAME + CURRENT_BALANCE_FILE_EXTENSION , 'r') as f:
            josh_balance_raw = f.read()
            #josh_balance = json.loads(josh_balance_raw)
            balances[JOSH_NAME] = json.loads(josh_balance_raw)

    except Exception as e:
        print("Loading current balances failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not load current balances'})


    # Validates the balances
    try:

        if balances[MEGAN_NAME]['balance'] is None:
            return jsonify({'status': '400', 'message': 'No Megan balances found'})

        if balances[JOSH_NAME]['balance'] is None:
            return jsonify({'status': '400', 'message': 'No Josh balances found'})

    except Exception as e:
        print("Validating balances failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not validate balances'})


    # Validates the sender has sufficient funds
    try:

        sender_balance = balances[data['from']]['balance']
        amount = int(data['amount'])


        if sender_balance < amount:
            print("next")
            return jsonify({'status': '400', 'message': 'Sender does not have enough balance'})

    except Exception as e:
        print("Validating sender balance failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not validate sender balance'})


    # Transfers the balance
    try:

        # Calculates new balances
        if data['from'] == MEGAN_NAME:
            balances[MEGAN_NAME] = int(balances[MEGAN_NAME]['balance']) - int(data['amount'])
            balances[JOSH_NAME] = int(balances[JOSH_NAME]['balance']) + int(data['amount'])

        elif data['from'] == JOSH_NAME:
            balances[MEGAN_NAME] = int(balances[MEGAN_NAME]['balance']) + int(data['amount'])
            balances[JOSH_NAME] = int(balances[JOSH_NAME]['balance']) - int(data['amount'])

    except Exception as e:
        print("Transfering balance failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not transfer balance'})


    # Saves the new balances
    try:
            
        with open(DATA_STORAGE_PATH + MEGAN_NAME + CURRENT_BALANCE_FILE_EXTENSION , 'w') as f:
            megan_map = {'balance': balances[MEGAN_NAME]}
            f.write(json.dumps(megan_map))
            #f.write(str(balances[MEGAN_NAME]))

        with open(DATA_STORAGE_PATH + JOSH_NAME + CURRENT_BALANCE_FILE_EXTENSION , 'w') as f:

            josh_map = {'balance': balances[JOSH_NAME]}
            f.write(json.dumps(josh_map))
           #f.write(str(balances[JOSH_NAME]))

    except Exception as e:
        print("Saving new balances failed: ", e)
        return jsonify({'status': '500', 'message': 'Could not save new balances'})

    return jsonify({'status': '200', 'message': 'Balance transferred'})

    
