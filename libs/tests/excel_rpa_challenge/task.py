from robo.libs.excel import create_workbook, open_workbook, Table


def create_new_workbook():
    workbook1 = open_workbook("Book1.xlsx")
    table = workbook1.worksheet("Sheet1").as_table(header=True)

    values = table.get_column("State")
    workbook2 = open_workbook("Book2.xlsx")
    table2 = workbook2.worksheet("Sheet1").as_table(header=True)

    table2.set_column("State Most Sold In", values)
    workbook3 = create_workbook("xlsx", "New Content")
    workbook3.worksheet("New Content").append_rows_to_worksheet(table2, header=True)
    workbook3.save("Book3.xlsx")

    print(table)


def read_people_from_excel() -> Table:
    table = open_workbook("challenge.xlsx").worksheet("Sheet1").as_table(header=True)
    return table


def fill_and_submit_form(person):
    #     Input Text    alias:First Name    ${person}[First Name]
    #     Input Text    alias:Last Name    ${person}[Last Name]
    #     Input Text    alias:Company Name    ${person}[Company Name]
    #     Input Text    alias:Role in Company    ${person}[Role in Company]
    #     Input Text    alias:Address    ${person}[Address]
    #     Input Text    alias:Email    ${person}[Email]
    #     Input Text    alias:Phone Number    ${person}[Phone Number]
    #     Click Button    Submit
    pass


def task_solve_challenge():
    #     Open Available Browser    http://rpachallenge.com/
    #     Download    http://rpachallenge.com/assets/downloadFiles/challenge.xlsx    overwrite=${TRUE}
    #     Click Button    Start
    people = read_people_from_excel()
    for person in people:
        fill_and_submit_form(person)
    #     Capture Element Screenshot    alias:Congratulations
    #     Sleep    2 seconds
    #     [Teardown]    Close All Browsers
    pass


if __name__ == "__main__":
    create_new_workbook()
