import traceback
try:
    print(variable_that_does_not_exist)
except Exception as e:
    print("----Hallo\n", traceback.format_exc(),"\n----Ende")