import data

def test_data_1():
    data_obj = data.Data.create()
    print(data_obj.other)

if __name__ == '__main__':
    test_data_1()