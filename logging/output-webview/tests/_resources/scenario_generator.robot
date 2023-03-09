*** Settings ***
Library     RPA.Desktop


*** Test Cases ***
My Test
    [Documentation]    Note that this test can be changed as needed. The idea
    ...    is that it can be changed as needed to provide .rfstream
    ...    files as needed.
    FOR    ${counter}    IN RANGE    1    1000
        ${show_err}=    Evaluate    $counter % 50 == 0
        IF    $show_err    Log    ${counter}    level=ERROR
    END

Screenshot test
    RPA.Desktop.Take Screenshot    output/test_screenshot.png    embed=True
