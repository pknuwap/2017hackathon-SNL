import xlrd
from functools import wraps


wb = xlrd.open_workbook("timetable.xls")
ws = wb.sheet_by_index(0)
ncol = ws.ncols
nlow = ws.nrows

print (str(ncol))
print (str(nlow))


for i in range(0,nlow):
    for j in range(0,ncol):   
        mongo.db.courselist.insert_one({
            '수강대상대학':str(ws.row_values(i)[0]),
            '수강대상학과':str(ws.row_values(i)[1]),
            '학수번호':str(ws.row_values(i)[2]),
            '분반':str(ws.row_values(i)[3]),
            '교과목명':str(ws.row_values(i)[4]),
            '영문교과목':str(ws.row_values(i)[5]),
            '학점':str(ws.row_values(i)[6]),
            '교과구분':str(ws.row_values(i)[7]),
            '공학인증구분':str(ws.row_values(i)[8]),
            '정원':str(ws.row_values(i)[9]),
            '현원':str(ws.row_values(i)[10]),
            '예비수강신청인원':str(ws.row_values(i)[11]),
            '외국어강의':str(ws.row_values(i)[12]),
            '담당교수':str(ws.row_values(i)[13]),
            '주야':str(ws.row_values(i)[14]),
            '학년':str(ws.row_values(i)[15]),
            '요일시간':str(ws.row_values(i)[16]),
            '개설학과':str(ws.row_values(i)[17]),
            '강의계획서':str(ws.row_values(i)[18]),
            '개설학과전화번호':str(ws.row_values(i)[19])
            })



            
            
