from tabulate import *
from corrector import *
from database import db


def start():
    db.start()
    while True:
        try:
            print(f"Active Category: [{db.temp_category}]")
            cmd = command(input("command: "))
            match cmd:
                case "create.category":
                    db.create_category(category=input("New Category: "), attributes=input("New Attributes: "))
                case "clear.category":
                    db.clear_category(category=input("Cleared Category: "))
                case "del.category":
                    db.del_category(category=input("Del Category: "))

                case "create.obj":
                    db.create_obj(attributes=input("Attributes: "), category=input("Category: "))
                case "change.obj":
                    db.change_obj(obj_id=input("Object Id: "),attributes=input("Attributes: "),category=input("Category: "))
                case "clear.obj":
                    db.clear_obj(obj_id=input("Object Id: "),category=input("Category: "))
                case "del.obj":
                    db.del_obj(obj_id=input("Object Id: "),category=input("Category: "))

                case "create.key":
                    db.create_key(key=input("Key: "),category=input("Category: "))
                case "del.key":
                    db.del_key(key=input("Key: "),category=input("Category: "))

                case "create.const":
                    db.create_const(constant=input("Constant: "),category=input("Category: "))
                case "del.const":
                    db.del_const(constant=input("Constant: "),category=input("Category: "))

                case "create.complete":
                    db.create_complete(complete=input("Complete: "),category=input("Category: "))
                case "del.complete":\
                    db.del_complete(complete=input("Complete: "),category=input("Category: "))

                case "datas":
                    print(db.get_datas(category=input("Category: ")))
                case "backup":
                    db.backup()
                case "load.backup": pass
                case "stop" | "exit" | "esc":
                    break
                case _:
                    print(f"Unknown Command: [{cmd}]")
        except KeyError:
            print("You have entered incorrect key values!")
        except TypeError:
            print("You have entered incorrect data types!")
        except ValueError:
            print("You have entered incorrect data in types!")
        except KeyboardInterrupt:
            print("Forced close!")
            db.shutdown()
            break


if __name__ == "__main__":
    start()
    db.shutdown()
