
import math
import pprint
import decimal
import fractions

numerator = ("47449023823422717451594836169381198840134089164995011450245185" +
             "61838777684717684085417406717376659694422247951574014327387976" +
             "8480709913455315809719544718248")
denominator = ("151034933727656572741457537643244123466736157365649904806452" +
               "295026919400951667087834668197436704093923364340930317605883" +
               "86010342390699617474201564040715683")

my_pi = fractions.Fraction (numerator + "/" + denominator)
pprint.pprint (my_pi)
pprint.pprint(float(my_pi))
math_pi = fractions.Fraction (math.pi)
pprint.pprint(math_pi)
pprint.pprint(float(math_pi))
pprint.pprint (my_pi - math_pi)
pprint.pprint (float (my_pi - math_pi))
