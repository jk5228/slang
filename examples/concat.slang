# Concatenate lists of strings.
def concat(strs) {
	res = "";
	for (str in strs) {
		res = res + str;
	}
	return res;
}