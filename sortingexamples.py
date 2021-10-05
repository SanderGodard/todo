#!/bin/python3
storage = "/home/sGodard/.config/todo/storage.txt"

def readData():
    try:
        data = []
        with open(storage, "r") as file:
            for line in file.readlines():
                data.append(line.replace("\n", "").strip())

        return data
    except:
        print("There was a problem reading the data from the storage file in: " + storage + "\n Please ensure the file and folder exists and permissions are correct")
        exit()


def sortData(data):
    done = ["-test"]
    for i in data:
        print("Jobber på: " + i[:8])
        if i[0] == "-":
            done.append(i)
        else:
            keys = ["|", "#", "/"]
            found = False
            for j in range(len(keys)):
                print("Sjekker om er i: " + keys[j])
                if i[0] == keys[j]:
                    print("Er riktig key")
                    done.reverse()
                    found2 = False
                    for l, k in enumerate(done):
                        print("Ser etter like")
                        if k[0] == keys[j] and found2 == False:
                            print("Fant den da, putter under siste")
                            done.insert(l, i)
                            found = True
                            found2 = True
                            break
                            #exit()
                    done.reverse()
                    if not found2:
                        print("Fant ingen like, putter nederst")
                        done.append(i)
                        found = True
                        break

            if not found:
                print("Har ingen key?")
                done.append("-" + i)

    done.pop(0)
    return done

def main():
    data = readData()
    for i in data:
        print(i)
    print("##############################")
    data = sortData(data)
    for i in data:
        print(i)

main()
