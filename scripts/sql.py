import argparse
import asyncio

from psqlpy import connect


async def main():
    parser = argparse.ArgumentParser(description="Execute SQL queries against the database")

    parser.add_argument("-f", "--file", dest="file", help="The file containing the SQL command to execute")

    args = parser.parse_args()


    pool = connect(dsn="postgres://postgres:test@localhost:5432/snippets")

    if not args.file:
        print("You must specify a file")
        exit(1)

    if args.file:
        print(f"Executing file: {args.file}")
        with open(args.file, encoding="utf-8") as file:
            content = file.read()

        connection = await pool.connection()
        await connection.execute_batch(content)


    pool.close()

    print("Completed")


if __name__ == "__main__":
    asyncio.run(main())