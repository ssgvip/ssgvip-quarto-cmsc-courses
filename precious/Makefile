
default:
	@type Makefile


zipfiles := 202120_Spring_2021.zip 202210_Fall_2021.zip 202220_Spring_2022.zip 202310_Fall_2022.zip 202320_Spring_2023.zip


202120:
	7z e 202120_Spring_2021.zip -y -o../docs/202120
	ren "..\\docs\\202120\\CMSC_591RoboticVision_Syllabus_Spring_2021.pdf" "CMSC_591_Syllabus_Spring_2021.pdf"
	ren ..\\docs\\202120\\CMSC_630_Syllabus_Spring_630.pdf CMSC_630_Syllabus_Spring_2021.pdf
	ren "..\\docs\\202120\\CMSC_257_Syllabus_Spring 2021.pdf" CMSC_257_Syllabus_Spring_202120.pdf
	rmdir /Q /S "..\\docs\\202120\\Spring 2021"

202210:
	7z e 202210_Fall_2021.zip -y -o../docs/202210

202220:
	7z e 202220_Spring_2022.zip -y -o../docs/202220

202310:
	7z e 202310_Fall_2022.zip -y -o../docs/202310

202320:
	7z e 202320_Spring_2023.zip -y -o../docs/202320

snapshot:
	7z a -spf snapshot ../docs/202120/*.*
	7z a -spf snapshot ../docs/202210/*.*
	7z a -spf snapshot ../docs/202220/*.*
	7z a -spf snapshot ../docs/202310/*.*
	7z a -spf snapshot ../docs/202320/*.*
