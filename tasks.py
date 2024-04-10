from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=200,
    )
    open_robot_order_website()
    orders = get_orders()
    fill_the_form(orders)
    archive_receipts()

def open_robot_order_website():
    """ Open robot order website """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """ Get orders from CSV file """
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    table = Tables()
    orders_table = table.read_table_from_csv("orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"])
    return orders_table

def close_annoying_modal():
    """ Close warning popup """
    page = browser.page()
    page.click("//button[text()='OK']")

def fill_the_form(orders):
    """ Fill the form """
    table = Tables()
    rows_number, columns_number = table.get_table_dimensions(orders)
    for index in range (0, rows_number):
        order_row = table.get_table_row(orders, index)
        close_annoying_modal()
        order(order_row)

def order(order):
    page = browser.page()
    page.select_option("#head", order["Head"])
    page.click("//input[@value='{index}']".format(index=order["Body"]))
    page.fill("//input[@placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#preview")
    page.click("#order")

    while not page.locator("#receipt").is_visible():
        page.click("#order")

    store_receipt_as_pdf(order["Order number"])
    screenshot_robot(order["Order number"])
    embed_screenshot_to_receipt(order["Order number"])
    page.click("#order-another")

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_text()
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, "output/receipt/receipt_{order}.pdf".format(order=order_number))

def screenshot_robot(order_number):
    page = browser.page()
    page.screenshot(path="output/preview/preview_{order}.png".format(order=order_number))

def embed_screenshot_to_receipt(order_number):
    pdf = PDF()
    pdf.add_files_to_pdf(["output/preview/preview_{order}.png".format(order=order_number)], "output/receipt/receipt_{order}.pdf".format(order=order_number), append=True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipt', 'receipts.zip', recursive=True)