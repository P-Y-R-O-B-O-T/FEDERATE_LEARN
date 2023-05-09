import os
import sys
#import traceback
#import matplotlib.pyplot as plot
#import gc
import time
import threading
import copy

from sklearn import svm
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline

DIRECTORY = "PREPROCESSED_DATA_2"
MAX_THREADS = 16
DATA = {}
MODELS = {}
TIME_REQ_EVERY_MODEL = {}
ACCURACIES = {}
DAY_DATE_MAP = {}

LOADED_TILL_NOW = 0

LOCK = threading.Lock()

def MAP_DATE_WITH_DAY_NO_OF_YEAR() :
    global DAY_DATE_MAP
    month_days_map = {
                        1:31,
                        2:28,
                        3:31,
                        4:30,
                        5:31,
                        6:30,
                        7:31,
                        8:31,
                        9:30,
                        10:31,
                        11:30,
                        12:31
                    }

    count = 1
    for _ in month_days_map.keys() :
        for __ in range(1, month_days_map[_]+1) :
            s1 = ""
            s2 = ""
            if _ < 10 : s1 = "0"+str(_)
            else : s1 = str(_)
            if __ < 10 : s2 = "0"+str(__)
            else : s2 = str(__)
            DAY_DATE_MAP[s1+s2] = count
            count += 1

def LOAD_DATA(location) :
    global DIRECTORY
    global DATA
    global LOCK
    global LOADED_TILL_NOW

    LOCK.acquire()
    loaded = LOADED_TILL_NOW
    LOADED_TILL_NOW += 1
    LOCK.release()

    loaded += 1

    print("[!] LOADING",loaded , location)

    file_handle = open(os.path.join(DIRECTORY,location)+".csv", "r")

    strings = file_handle.readlines()

    headers = strings[0]
    temp_data = strings[1:]

    for _ in range(len(temp_data)) :
        temp_data[_] = temp_data[_].split(",")

    for _ in range(len(temp_data)) :
        for __ in range(len(temp_data[_])) :
            temp_data[_][__] = eval(temp_data[_][__])
            if __ == 0 :
                temp_data[_][__] = round(temp_data[_][__],-6)

    data = CONVERT_TO_DAY_FORMAT(temp_data, location)
    DATA[location] = data

    print("[#] LOADED", loaded, location)

def CONVERT_TO_DAY_FORMAT(temp_data, location) :
    global DAY_DATE_MAP
    data = []
    tick_count = 1
    data.append(copy.deepcopy(temp_data[0]))
    for _ in range(1, len(temp_data)) :
        if data[-1][0] == temp_data[_][0] :
            for __ in range(1, len(temp_data[_])) :
                data[-1][__] += temp_data[_][__]
            tick_count += 1
        else :
            for __ in range(2, len(data[-1])) :
                data[-1][__] /= tick_count
            data.append(copy.deepcopy(temp_data[_]))
            tick_count = 1

    for _ in range(len(data)) :
        if str(data[_][0])[4:8] in DAY_DATE_MAP :
            data[_][0] = DAY_DATE_MAP[str(data[_][0])[4:8]]

    return data

def GET_RANGE(no_locations) :
    arg = sys.argv
    part_size = no_locations//int(arg[2])
    if arg[1] == arg[2] :
        lower_limit = part_size*(int(arg[1]) - 1)
        upper_limit = no_locations
        return [lower_limit, upper_limit]
    elif arg[1] < arg[2] :
        lower_limit = part_size*(int(arg[1]) - 1)
        upper_limit = part_size*(int(arg[1]))
        return [lower_limit, upper_limit]

def LOAD_ALL_DATA() :
    temp_file = open("locations.txt", "r")
    locations = eval(temp_file.read())
    threads = []
    load_range = GET_RANGE(len(locations))
    for _ in range(load_range[0], load_range[1]) :
        threads.append(threading.Thread(target=LOAD_DATA, args=(str(locations[_]),)))
        threads[-1].run()

def CREATE_TRAINING_SET() :
    global DATA
    global FEATURES
    global TARGETS
    FEATURES = {}
    TARGETS = {}

    feature_index = 5
    
    for _ in list(DATA.keys()) :
        print("[~] CREATING TRAINING SET FOR", _)
        FEATURES[_] = []
        TARGETS[_] = []
        location_data = DATA[_]
        features = []
        targets = []
        for __ in range(5, len(location_data)) :
            temp_features = []
            for temp_huhu in range(len(location_data[0])) :
                temp_features.append(0)
            temp_target = location_data[__][feature_index]
            for ___ in range(__-5, __) :
                for ____ in range(len(location_data[0])) :
                    #if ____ != 0 :
                    temp_features[____] += location_data[___][____]
            for temp_huhu in range(len(temp_features)) :
                temp_features[temp_huhu] /= 5
            features.append(temp_features)
            targets.append(temp_target)
        FEATURES[_] = features
        TARGETS[_] = targets
        print("[~] CREATED TRAINING SET FOR", _)

def CREATE_MODELS() :
    global MODELS

    MODELS["SVR 1 Degree"] = make_pipeline(PolynomialFeatures(1), svm.SVR())
    MODELS["SVR 2 Degree"] = make_pipeline(PolynomialFeatures(2), svm.SVR())
    MODELS["SVR 3 Degree"] = make_pipeline(PolynomialFeatures(3), svm.SVR())
    MODELS["SVR 4 Degree"] = make_pipeline(PolynomialFeatures(4), svm.SVR())
    MODELS["SVR 5 Degree"] = make_pipeline(PolynomialFeatures(5), svm.SVR())

    MODELS["KNNR 1 Degree 2 Neighbors"] = make_pipeline(PolynomialFeatures(1), KNeighborsRegressor(n_neighbors=2))
    MODELS["KNNR 1 Degree 3 Neighbors"] = make_pipeline(PolynomialFeatures(1), KNeighborsRegressor(n_neighbors=3))
    MODELS["KNNR 1 Degree 5 Neighbors"] = make_pipeline(PolynomialFeatures(1), KNeighborsRegressor(n_neighbors=5))
    MODELS["KNNR 1 Degree 7 Neighbors"] = make_pipeline(PolynomialFeatures(1), KNeighborsRegressor(n_neighbors=7))
    MODELS["KNNR 1 Degree 10 Neighbors"] = make_pipeline(PolynomialFeatures(1), KNeighborsRegressor(n_neighbors=10))
    MODELS["KNNR 2 Degree 2 Neighbors"] = make_pipeline(PolynomialFeatures(2), KNeighborsRegressor(n_neighbors=2))
    MODELS["KNNR 2 Degree 3 Neighbors"] = make_pipeline(PolynomialFeatures(2), KNeighborsRegressor(n_neighbors=3))
    MODELS["KNNR 2 Degree 5 Neighbors"] = make_pipeline(PolynomialFeatures(2), KNeighborsRegressor(n_neighbors=5))
    MODELS["KNNR 2 Degree 7 Neighbors"] = make_pipeline(PolynomialFeatures(2), KNeighborsRegressor(n_neighbors=7))
    MODELS["KNNR 2 Degree 10 Neighbors"] = make_pipeline(PolynomialFeatures(2), KNeighborsRegressor(n_neighbors=10))
    MODELS["KNNR 3 Degree 2 Neighbors"] = make_pipeline(PolynomialFeatures(3), KNeighborsRegressor(n_neighbors=2))
    MODELS["KNNR 3 Degree 3 Neighbors"] = make_pipeline(PolynomialFeatures(3), KNeighborsRegressor(n_neighbors=3))
    MODELS["KNNR 3 Degree 5 Neighbors"] = make_pipeline(PolynomialFeatures(3), KNeighborsRegressor(n_neighbors=5))
    MODELS["KNNR 3 Degree 7 Neighbors"] = make_pipeline(PolynomialFeatures(3), KNeighborsRegressor(n_neighbors=7))
    MODELS["KNNR 3 Degree 10 Neighbors"] = make_pipeline(PolynomialFeatures(3), KNeighborsRegressor(n_neighbors=10))
    MODELS["KNNR 4 Degree 2 Neighbors"] = make_pipeline(PolynomialFeatures(4), KNeighborsRegressor(n_neighbors=2))
    MODELS["KNNR 4 Degree 3 Neighbors"] = make_pipeline(PolynomialFeatures(4), KNeighborsRegressor(n_neighbors=3))
    MODELS["KNNR 4 Degree 5 Neighbors"] = make_pipeline(PolynomialFeatures(4), KNeighborsRegressor(n_neighbors=5))
    MODELS["KNNR 4 Degree 7 Neighbors"] = make_pipeline(PolynomialFeatures(4), KNeighborsRegressor(n_neighbors=7))
    MODELS["KNNR 4 Degree 10 Neighbors"] = make_pipeline(PolynomialFeatures(4), KNeighborsRegressor(n_neighbors=10))
    MODELS["KNNR 5 Degree 2 Neighbors"] = make_pipeline(PolynomialFeatures(5), KNeighborsRegressor(n_neighbors=2))
    MODELS["KNNR 5 Degree 3 Neighbors"] = make_pipeline(PolynomialFeatures(5), KNeighborsRegressor(n_neighbors=3))
    MODELS["KNNR 5 Degree 5 Neighbors"] = make_pipeline(PolynomialFeatures(5), KNeighborsRegressor(n_neighbors=5))
    MODELS["KNNR 5 Degree 7 Neighbors"] = make_pipeline(PolynomialFeatures(5), KNeighborsRegressor(n_neighbors=7))
    MODELS["KNNR 5 Degree 10 Neighbors"] = make_pipeline(PolynomialFeatures(5), KNeighborsRegressor(n_neighbors=10))

    MODELS["RFR 1 Degree 2 Depth"] = make_pipeline(PolynomialFeatures(1), RandomForestRegressor(max_depth=2, random_state=0))
    MODELS["RFR 2 Degree 2 Depth"] = make_pipeline(PolynomialFeatures(2), RandomForestRegressor(max_depth=2, random_state=0))
    MODELS["RFR 3 Degree 2 Depth"] = make_pipeline(PolynomialFeatures(3), RandomForestRegressor(max_depth=2, random_state=0))
    MODELS["RFR 4 Degree 2 Depth"] = make_pipeline(PolynomialFeatures(4), RandomForestRegressor(max_depth=2, random_state=0))
    MODELS["RFR 5 Degree 2 Depth"] = make_pipeline(PolynomialFeatures(5), RandomForestRegressor(max_depth=2, random_state=0))
    MODELS["RFR 1 Degree 3 Depth"] = make_pipeline(PolynomialFeatures(1), RandomForestRegressor(max_depth=3, random_state=0))
    MODELS["RFR 2 Degree 3 Depth"] = make_pipeline(PolynomialFeatures(2), RandomForestRegressor(max_depth=3, random_state=0))
    MODELS["RFR 3 Degree 3 Depth"] = make_pipeline(PolynomialFeatures(3), RandomForestRegressor(max_depth=3, random_state=0))
    MODELS["RFR 4 Degree 3 Depth"] = make_pipeline(PolynomialFeatures(4), RandomForestRegressor(max_depth=3, random_state=0))
    MODELS["RFR 5 Degree 3 Depth"] = make_pipeline(PolynomialFeatures(5), RandomForestRegressor(max_depth=3, random_state=0))
    MODELS["RFR 1 Degree 5 Depth"] = make_pipeline(PolynomialFeatures(1), RandomForestRegressor(max_depth=5, random_state=0))
    MODELS["RFR 2 Degree 5 Depth"] = make_pipeline(PolynomialFeatures(2), RandomForestRegressor(max_depth=5, random_state=0))
    MODELS["RFR 3 Degree 5 Depth"] = make_pipeline(PolynomialFeatures(3), RandomForestRegressor(max_depth=5, random_state=0))
    MODELS["RFR 4 Degree 5 Depth"] = make_pipeline(PolynomialFeatures(4), RandomForestRegressor(max_depth=5, random_state=0))
    MODELS["RFR 5 Degree 5 Depth"] = make_pipeline(PolynomialFeatures(5), RandomForestRegressor(max_depth=5, random_state=0))
    
    ####################################
    ## MODELS THAT TAKE A LOT OF TIME ##
    ####################################
    #
    MODELS["RFR 1 Degree 7 Depth"] = make_pipeline(PolynomialFeatures(1), RandomForestRegressor(max_depth=7, random_state=0))
    MODELS["RFR 2 Degree 7 Depth"] = make_pipeline(PolynomialFeatures(2), RandomForestRegressor(max_depth=7, random_state=0))
    MODELS["RFR 3 Degree 7 Depth"] = make_pipeline(PolynomialFeatures(3), RandomForestRegressor(max_depth=7, random_state=0))
    MODELS["RFR 4 Degree 7 Depth"] = make_pipeline(PolynomialFeatures(4), RandomForestRegressor(max_depth=7, random_state=0))
    MODELS["RFR 5 Degree 7 Depth"] = make_pipeline(PolynomialFeatures(5), RandomForestRegressor(max_depth=7, random_state=0))
    MODELS["RFR 1 Degree 10 Depth"] = make_pipeline(PolynomialFeatures(1), RandomForestRegressor(max_depth=10, random_state=0))
    MODELS["RFR 2 Degree 10 Depth"] = make_pipeline(PolynomialFeatures(2), RandomForestRegressor(max_depth=10, random_state=0))
    MODELS["RFR 3 Degree 10 Depth"] = make_pipeline(PolynomialFeatures(3), RandomForestRegressor(max_depth=10, random_state=0))
    MODELS["RFR 4 Degree 10 Depth"] = make_pipeline(PolynomialFeatures(4), RandomForestRegressor(max_depth=10, random_state=0))
    MODELS["RFR 5 Degree 10 Depth"] = make_pipeline(PolynomialFeatures(5), RandomForestRegressor(max_depth=10, random_state=0))

def TRAIN_MODELS() :
    global FEATURES
    #for _ in list(FEATURES.keys()) :
    #    print("[$] TRAINING AND TESTING", _)
    #    TRAIN_MODEL(_)
    #    print("")

    location_list = list(FEATURES.keys())
    current = 0
    while current < len(location_list) :
        threads = []
        for _ in range(MAX_THREADS) :
            if current < len(location_list) :
                print("[$] TRAINING AND TESTING", location_list[current])
                threads.append(threading.Thread(target=TRAIN_MODEL, args=(location_list[current],)))
                threads[-1].start()
            current += 1
        for _ in threads :
            _.join()

def TRAIN_MODEL(location) :
    global FEATURES, TARGETS, MODELS, ACCURACIES, TIME_REQ_EVERY_MODEL

    models = copy.deepcopy(MODELS)

    accuracies = {}
    for _ in list(models.keys()) :
        accuracies[_] = 0
    initial_time = time.time()
    ################################################333
    #for _ in models :
    #    threads.append(threading.Thread(target=models[_].fit, args=(FEATURES[location], TARGETS[location])))
    #    threads[-1].start()
    #for _ in threads :
    #    _.join()

    #TIME_REQ_EVERY_MODEL[location] = time.time() - initial_time

    #threads = []

    #for _ in models :
    #    threads.append(threading.Thread(target=GET_ACCURACY, args=(accuracies, _, models, location)))
    #    threads[-1].start()
    #for _ in threads :
    #    _.join()

    ACCURACIES[location] = accuracies

    # getting max accuracy for svr
    threads = []
    for _ in range(1, 6) :
        threads.append(threading.Thread(target=models["SVR "+str(_)+" Degree"].fit, args=(FEATURES[location], TARGETS[location])))
        threads[-1].start()
    for _ in range(len(threads)) :
        threads[_].join()
    threads = []
    for _ in range(1, 6) :
        threads.append(threading.Thread(target=GET_ACCURACY, args=(accuracies, "SVR "+str(_)+" Degree", models, location)))
        threads[-1].start()
    for _ in range(len(threads)) :
        threads[_].join()

    max_degree_svr = 1
    max_accuracy = 0
    for _ in range(1, 6) :
        if accuracies["SVR "+str(_)+" Degree"] > max_accuracy :
            max_accuracy = accuracies["SVR "+str(_)+" Degree"]
            max_degree_svr = _

    # getting amx accuracy for knn
    threads = []
    for _ in range(1, 6) :
        threads.append(threading.Thread(target=models["KNNR "+str(_)+" Degree 2 Neighbors"].fit, args=(FEATURES[location], TARGETS[location])))
        threads[-1].start()
    for _ in range(len(threads)) :
        threads[_].join()
    threads = []
    for _ in range(1, 6) :
        threads.append(threading.Thread(target=GET_ACCURACY, args=(accuracies, "KNNR "+str(_)+" Degree 2 Neighbors", models, location)))
        threads[-1].start()
    for _ in range(len(threads)) :
        threads[_].join()


    max_degree_knnr = 1
    max_accuracy = 0
    for _ in range(1, 6) :
        if accuracies["KNNR "+str(_)+" Degree 2 Neighbors"] > max_accuracy :
            max_accuracy = accuracies["KNNR "+str(_)+" Degree 2 Neighbors"]
            max_degree_knnr = _

    threads = []
    for _ in [2, 3, 5, 7, 10] :
        threads.append(threading.Thread(target=models["KNNR "+str(max_degree_knnr)+" Degree "+str(_)+" Neighbors"].fit, args=(FEATURES[location], TARGETS[location])))
        threads[-1].start()
    for _ in range(len(threads)) :
        threads[_].join()
    threads  = []
    for _ in [2, 3, 5, 7, 10] :
        threads.append(threading.Thread(target=GET_ACCURACY, args=(accuracies, "KNNR "+str(max_degree_knnr)+" Degree "+str(_)+" Neighbors", models, location)))
        threads[-1].start()
    for _ in range(len(threads)) :
        threads[-1].join()

    # getting amx accuracy for RFR
    threads = []
    for _ in range(1, 6) :
        threads.append(threading.Thread(target=models["RFR "+str(_)+" Degree 2 Depth"].fit, args=(FEATURES[location], TARGETS[location])))
        threads[-1].start()
    for _ in range(len(threads)) :
        threads[_].join()
    threads = []
    for _ in range(1, 6) :
        threads.append(threading.Thread(target=GET_ACCURACY, args=(accuracies, "RFR "+str(_)+" Degree 2 Depth", models, location)))
        threads[-1].start()
    for _ in range(len(threads)) :
        threads[_].join()

    max_degree_rfr = 1
    max_accuracy = 0
    for _ in range(1, 6) :
        if accuracies["RFR "+str(_)+" Degree 2 Depth"] > max_accuracy :
            max_accuracy = accuracies["RFR "+str(_)+" Degree 2 Depth"]
            max_degree_rfr = _

    threads = []
    for _ in [2, 3, 5, 7, 10] :
        threads.append(threading.Thread(target=models["RFR "+str(max_degree_rfr)+" Degree "+str(_)+" Depth"].fit, args=(FEATURES[location], TARGETS[location])))
        threads[-1].start()
    for _ in range(len(threads)) :
        threads[_].join()
    threads  = []
    for _ in [2, 3, 5, 7, 10] :
        threads.append(threading.Thread(target=GET_ACCURACY, args=(accuracies, "RFR "+str(max_degree_rfr)+" Degree "+str(_)+" Depth", models, location)))
        threads[-1].start()
    for _ in range(len(threads)) :
        threads[-1].join()

    TIME_REQ_EVERY_MODEL[location] = time.time() - initial_time
    ACCURACIES[location] = accuracies


def GET_ACCURACY(accuracies, model, models, location) :
    global FEATURES, TARGETS
    score = models[model].score(FEATURES[location], TARGETS[location])
    accuracies[model] = score

def SAVE_DATA(time_) :
    global MODELS
    global TIME_REQ_EVERY_MODEL
    global ACCURACIES

    file_accuracies = open("ACCURACY_OP.txt", "w")
    file_accuracies.write(str(ACCURACIES))
    file_accuracies.flush()
    file_accuracies.close()

    file_time = open("TIME_REQ.txt", "w")
    file_time.write(str(TIME_REQ_EVERY_MODEL))
    file_time.flush()
    file_time.close()

    file_time_ = open("TIME.txt", "w")
    file_time_.write(str(time.time()-time_))
    file_time_.flush()
    file_time_.close()

if __name__ == "__main__" :
    t = time.time()
    MAP_DATE_WITH_DAY_NO_OF_YEAR()
    LOAD_ALL_DATA()
    CREATE_MODELS()
    CREATE_TRAINING_SET()
    TRAIN_MODELS()
    print("[*] TOTAL TIME TAKEN",time.time()-t)
    SAVE_DATA(t)
