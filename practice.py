import psycopg
#資料庫連線參數
conn_str = '''
    host=localhost port=5432 dbname=school user=postgres password=0000
'''
#1. 姓名搜尋學生
def select_student_by_name(name: str):
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT * FROM niu.student WHERE name = %s
            ''', (name,))
            rows = cur.fetchall() #取得所有結果
            return rows
#2. 新增學生
def add_student(name: str, dept_id: int):
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO niu.student (name, dept_id) VALUES (%s, %s)
            ''', (name, dept_id)) 
#3. 刪除學生
def delete_student(name: str):
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                DELETE FROM niu.student WHERE name = %s
            ''', (name,))
#主程式
if __name__ == "__main__":
    print("1. 以姓名(Tony)搜尋學生")
    print(select_student_by_name("Tony"))

    print("\n2. 新增學生(name=Tony, dept_id=2)")
    add_student("Tony", 2)

    print("\n3. 以姓名(Tony)搜尋學生")
    print(select_student_by_name("Tony"))

    print("\n4. 刪除學生 Tony")
    delete_student("Tony")

    print("\n5. 以姓名(Tony)搜尋學生")
    print(select_student_by_name("Tony"))