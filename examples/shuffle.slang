# Fisher-Yates shuffle an array.
def shuffle(arr) {
	for (i in 0..size(arr)-2) {
		j = floor(random()*(size(arr)-i))+i;
		temp = arr[i];
		arr[i] = arr[j];
		arr[j] = temp;
	}
	return arr;
}