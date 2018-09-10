from get_file_create_modify_time import *


def delete_all_file_in_folder(parent_folder_path):
    for folderName, subfolders, filenames in os.walk(parent_folder_path):
        # print('The current folder is ' + folderName)
    
        for filename in filenames:
            if filename.endswith('.csv'):
                # print('File inside ' + folderName + ": " + filename)
                file_path = os.path.join(folderName, filename)
                file_create_date = last_modify_date(file_path)
                # print('File path ' + file_path)
                # print('File creation date ' + file_create_date)
                os.unlink(file_path)
                print(filename + " deleted.")

if __name__ == '__main__':
    order_report_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                        "Shopee 2016.4.12\\2016.4.23 Data Visualization\\Order"
    listing_report_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                        "Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing"
    pricing_report_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                        "Shopee 2016.4.12\\2016.4.23 Data Visualization\\Pricing"
    product_view_report_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                        "Shopee 2016.4.12\\2016.4.23 Data Visualization\\ProductView"

    delete_all_file_in_folder(order_report_path)
    delete_all_file_in_folder(listing_report_path)
    delete_all_file_in_folder(pricing_report_path)
    delete_all_file_in_folder(product_view_report_path)