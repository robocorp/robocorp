*** Settings ***
Documentation       Tests for the Output View.

Library             RPA.Browser.Playwright
Library             String
Library             json
Library             RPA.FileSystem
Library             Collections
Library             ./uris.py

Test Teardown       Close Browser


*** Variables ***
# ${HEADLESS}    False
${HEADLESS}     True


*** Test Cases ***
Test Scenario 1 simple
    [Documentation]
    ...    A simple scenario where the output view is opened with a
    ...    single test which passed without any keywords.
    Open Output View For Tests
    Setup Scenario    ${CURDIR}/_resources/case1.rfstream
    Check Labels    1
    Check Tree Items Text    Robot1.Simple Task

Test Scenario 2 restart
    [Documentation]
    ...    A simple scenario where the output view is opened with a
    ...    single test which passed without any keywords (with ignored restart).
    Open Output View For Tests
    Setup Scenario    ${CURDIR}/_resources/case2.rfstream
    Check Labels    1
    Check Tree Items Text    Robot1.Simple Task

Test Scenario 3 only restart
    [Documentation]
    ...    A simple scenario where the output view is opened with a
    ...    single test which passed without any keywords (just with restart).
    Open Output View For Tests
    Setup Scenario    ${CURDIR}/_resources/case3.rfstream
    Check Labels    1
    Check Tree Items Text    Robot1.Simple Task

Test Scenario 4 screenshot
    [Documentation]
    ...    A scenario with a screenshot.
    Open Output View For Tests
    Setup Scenario    ${CURDIR}/_resources/case4.rfstream
    Check Image
    Check Tree Items Text    Scenario Generator.Screenshot test
    ...    KEYWORD - RPA.Desktop.Take Screenshot | output/test_screenshot.png | embed\=True
    ...    Saved screenshot as 'output\\test_screenshot.png'
    ...    ${EMPTY}

Test Scenario 5 filtering NOT RUN
    [Documentation]
    ...    A scenario with many elements in a FOR (some not run).
    Open Output View For Tests
    Setup Scenario    ${CURDIR}/_resources/case5.rfstream
    # Default filtering is PASS.
    Check Labels From Pass Onwards

    # Change filtering to NOT RUN.
    RPA.Browser.Playwright.Select Options By    \#filterLevel    value    NOT RUN
    Check Labels From Not Run Onwards

Test Scenario 5 hide too many loops
    [Documentation]
    ...    A scenario with many elements in a FOR (some not run).
    Open Output View For Tests
    Setup Scenario    ${CURDIR}/_resources/case5.rfstream
    ${text_items}=    Get Text From Labels
    BuiltIn.Should Contain X Times    ${text_items}    HIDDEN    19


*** Keywords ***
Check Labels From Not Run Onwards
    ${text_items}=    Get Text From Labels
    ${text_items}=    Remove Duplicates    ${text_items}
    Should Contain    ${text_items}    NOT RUN
    ${expected}=    Evaluate    ['PASS', 'LOG INFO', 'NOT RUN', 'LOG ERROR', 'HIDDEN', '...']
    Should Be Equal As Strings    ${expected}    ${text_items}

Check Labels From Pass Onwards
    ${text_items}=    Get Text From Labels
    ${text_items}=    Remove Duplicates    ${text_items}
    Should Not Contain    ${text_items}    NOT RUN
    ${expected}=    Evaluate    ['PASS', 'LOG INFO', 'LOG ERROR', 'HIDDEN', '...']
    Should Be Equal As Strings    ${expected}    ${text_items}

Check Integers Equal
    [Arguments]    ${a}    ${b}
    ${a}=    Convert To Integer    ${a}
    ${b}=    Convert To Integer    ${b}
    Builtin.Should Be Equal    ${a}    ${b}

Open Output View For Tests
    ${curdir_proper_slashes}=    Replace String    ${CURDIR}    \\    /
    ${filepath}=    Set Variable    ${curdir_proper_slashes}/../dist-test/index.html
    ${exists}=    RPA.FileSystem.Does File Exist    ${filepath}
    Should Be True    ${exists}    File "${filepath}"" does not exist (distribution does not seem to be built).

    ${fileuri}=    uris.From Fs Path    ${filepath}
    RPA.Browser.Playwright.Set Browser Timeout    3
    Log To Console    fileuri=${fileuri}
    Open Browser    url=${fileuri}    headless=${HEADLESS}

Setup Scenario
    [Arguments]    ${filename}
    ${contents}=    RPA.FileSystem.Read File    ${filename}
    ${contents_as_json}=    json.Dumps    ${contents}

    Evaluate JavaScript    ${None}
    ...    ()=>{
    ...    window['setupScenario'](${contents_as_json});
    ...    }

Get Text From Elements
    [Arguments]    ${locator}
    ${elements}=    RPA.Browser.Playwright.Get Elements     ${locator}
    ${lst}=    Builtin.Create List
    FOR    ${element}    IN    @{elements}
        ${txt}=    RPA.Browser.Playwright.Get Text    ${element}
        Append To List    ${lst}    ${txt}
    END
    RETURN    ${lst}

Get Text From Tree Items
    ${txt}=    Get Text From Elements    .span_link
    RETURN    ${txt}

Get Text From Labels
    ${txt}=    Get Text From Elements    .label
    RETURN    ${txt}

Check Labels
    [Arguments]    ${expected_number_of_labels}
    ${element_count}=    RPA.Browser.Playwright.Get Element Count    .label
    Check Integers Equal    ${expected_number_of_labels}    ${element_count}

Check Tree Items Text
    [Arguments]    @{expected_text_items}
    ${text_items}=    Get Text From Tree Items
    Should Be Equal    ${text_items}    ${expected_text_items}

Check Image
    ${element_count}=    RPA.Browser.Playwright.Get Element Count    img
    Check Integers Equal    1    ${element_count}
