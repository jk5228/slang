(
	( def f(x)
		(
			( if ( < x 0 )
				(
					( print("what") )
					( return )
				)
				(
					( print(x) )
					( f( ( - x 1 ) ) )
				)
			)
		)
	)
	( f(10) )
)