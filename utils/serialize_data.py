
def serialize_data(input_data):
    # Sort the input data by the second element and then the first element of each tuple
    sorted_data = sorted(input_data, key=lambda x: (x[1], x[0]))
    return sorted_data
