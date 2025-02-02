-- Write query to get count of assignments in each grade
SELECT
    student_id,
    grade,
    COUNT(*) AS total_assignments
FROM
    assignments
WHERE
    state = 'GRADED'
GROUP BY
    student_id,
    grade
ORDER BY
    student_id,
    grade;