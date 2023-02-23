select
 *
FROM
 dbo.ex_course_catalog
WHERE
  1=1
  and subject='CMSC'
  and academic_year='9999'
order BY
  course_identification

