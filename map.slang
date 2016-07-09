(
	( def map ( f arr )
		(
			( = res ( array( ( size(arr) ) ) ) )
			( for ( i in ( range( 0, ( size(arr) ) ) ) )
				(
					( = ( res[i] ) ( f( ( arr[i] ) ) ) )
				)
			)
			( return res )
		)
	)
	( def square (x)
		(
			( return ( * x x ) )
		)
	)
	( print( ( map( square ( range(0,10) ) ) ) ) )
)