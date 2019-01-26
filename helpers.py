""" Module to hold the helper functions """

def args_salah_converter(index, data_item):
	""" Function to convert arguements for salah buttons """
	args = {"text": data_item}

	if index%2:
		args["deselected_color"] = [1/255, 100/255, 140/255, 1]
		args["selected_color"] = [1/255, 100/255, 140/255, 1]
	else:
		args["deselected_color"] =  [62/255, 114/255, 135/255, 1]
		args["selected_color"] = [62/255, 114/255, 135/255, 1]

	return args