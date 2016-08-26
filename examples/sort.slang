# Sort arrays.
def quicksort(arr) {
	if (size(arr) < 2) {
		return arr;
	}
	else {
		j = floor(random()*(size(arr)-1));
		pivot = arr[j];
		lo = {i in arr: i < pivot};
		same = {i in arr: i == pivot};
		hi = {i in arr: i > pivot};
		print(lo);
		print(same);
		print(hi);
		lo = quicksort(lo);
		hi = quicksort(hi);
		return lo + same + hi;
	}
}