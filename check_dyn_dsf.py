#!/usr/bin/python2.6
# -*- coding: utf8 -*-

#########################################
# DynECT DSF monitoring                 #
# Using DynectDNS API from DynDNS       #
#                                       #
# By Clément Bruneteau                  #
#                                       #
# version : 0.1.0                       #
# last change : 02 october 2014         #
#                                       #
# usage : check_dyn_dsf.py <dsfname>    #
#########################################


from DynectDNS import DynectRest
import sys
import os

api = DynectRest()
args = {
    'customer_name': 'your_customername',
    'user_name': 'your_username',
    'password': 'your_password',
}
RETURNSTRINGS = { 0: "OK", 1: "WARNING", 2: "CRITICAL", 3: "UNKNOWN" }
rulesets_list = []
responsepools_list = [[] for i in range(2)]
send_nsca_bin = "/srv/eyesofnetwork/nagios/bin/send_nsca"
send_nsca_etc = "/srv/eyesofnetwork/nagios/etc/send_nsca.cfg"


if len(sys.argv) == 1:
	print("usage : check_dyn_dsf.py <dsfname>")
	sys.exit(3)
else:
	url = '/REST/DSF/?label=' + sys.argv[1]



def session(action):
    if action == "login":
        response = api.execute('/REST/Session/', 'POST', args)
        if response['status'] != 'success':
            print("UNKNOWN : Login to API failed !")
            sys.exit(3)
    
    elif action == "logout":
        api.execute('/REST/Session/', 'DELETE')



def get_dsf():
    dsf_url_array = api.execute(url, 'GET')

    if not dsf_url_array['data']:
        print("UNKNOWN : DSF " + url + " does not exist!")
        sys.exit(3)

    dsf_url = dsf_url_array['data'][0]
    dsf = api.execute('{0}'.format(dsf_url), 'GET')
    return dsf



def get_dsf_rulesets():
    dsf = get_dsf()
    
    nb_rulesets = 0
    while nb_rulesets < len(dsf['data']['rulesets']):
        nb_responsepools = 0
        
        dsf_ruleset = dsf['data']['rulesets'][nb_rulesets]
        rulesets_list.append(dsf_ruleset['label'])

        while nb_responsepools < len(dsf_ruleset['response_pools']):
            dsf_response_pool = dsf_ruleset['response_pools'][nb_responsepools]
            responsepools_list[nb_rulesets].append((dsf_response_pool['label'],dsf_response_pool['status']))
                
            nb_responsepools += 1
        
        nb_rulesets += 1

    return nb_rulesets



def get_results(i):
    y = 0
    response_value = 0
    oldlocation_rulesets = responsepools_list[i][0][0]
    newlocation_rulesets = 'ok'
        
    while responsepools_list[i][y][1] != 'ok':
        if y < (len(responsepools_list[i]) - 1):
            response_value = 1
            newlocation_rulesets = responsepools_list[i][y+1][0]
        elif y == (len(responsepools_list[i]) - 1):
            response_value = 2
            newlocation_rulesets = 'no'
            break
        y += 1

    return (response_value, oldlocation_rulesets, newlocation_rulesets)




def main():
    
    session("login")
    
    nb_rulesets = get_dsf_rulesets()

    session("logout")
    
    return_value = 0
    i = 0
    command_string = 'echo "' + sys.argv[1] + ';;rulesets_DynDNS;;' + str(return_value) + ';'


    while i < nb_rulesets:
        
        results = get_results(i)


        if return_value < results[0]:
            return_value = results[0]


        response_string = rulesets_list[i] + ' ruleset is ' + RETURNSTRINGS[results[0]] + ' : '

        if results[2] == 'ok':
            response_string = response_string + results[1] + ' is active response pools !'
        elif results[2] == 'no':
            response_string = response_string + 'no response pools active !'
        else:
            response_string = response_string + results[1] + ' response pools migrate to ' + results[2] + ' !'

            
	command_string = command_string + response_string + '\\n'
        print(response_string)
        i += 1
   

    command_string = command_string + '" | ' + send_nsca_bin + ' -H localhost -c ' + send_nsca_etc + ' -d ";;"'
    os.system(command_string)
    sys.exit(return_value)


if __name__ == '__main__':
        main()
