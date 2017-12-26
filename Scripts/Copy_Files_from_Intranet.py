import glob
import shutil
from Scripts.Get_File_Create_Modify_Time import *
from Scripts.Get_Particular_Date import *


# listdir有个毛病，会把隐藏文件都加上，所以需要排除
def listdir_not_hidden(path):
    return glob.glob(os.path.join(path, '*'))


# 判断文件夹内所有文件的last update time
def check_last_update_date_within_folder(checked_path):
    folder_name = os.path.basename(checked_path)
    if not listdir_not_hidden(checked_path):
        return False
    else:
        for filename in listdir_not_hidden(checked_path):
            file_path = os.path.join(checked_path, filename)
            file_last_update_date = last_modify_date(file_path)
            today_date = get_today_date().strftime("%Y-%m-%d")
            if file_last_update_date != today_date:
                print("intranet " + folder_name + ' old data not deleted!')
                return False
                break
        # print('All files in ' + folder_name + ' are latest data.')
        return True


# 判断文件夹内是否包含所有国家
def check_all_country_available(checked_path):
    folder_name = os.path.basename(checked_path)
    if not listdir_not_hidden(checked_path):
        return False
    else:
        country_list = []
        for filename in listdir_not_hidden(checked_path):
            if filename.endswith('.csv'):
                # 判断是order/listing/pricing folder
                file_type = os.path.basename(checked_path).split('_')[0]

                # 创建一个判断字典
                file_type_list = {
                    'order': os.path.basename(filename).split('_')[2][:2].upper(),
                    'listing': os.path.basename(filename).split('_')[0],
                    'pricing': os.path.basename(filename).split('_')[2][:2].upper()
                }

                country_name = file_type_list[file_type]

                if country_name not in country_list:
                    country_list.append(country_name)
                country_list.sort()

        if country_list == ['ID', 'MY', 'PH', 'SG', 'TH', 'TW']:
            print("All country data in " + folder_name + " are downloaded.")
            return True
        else:
            return False


# 判断文件夹是否非空、是否都是今天、是否所有国家都齐备
def check_data_validation(path):
    if listdir_not_hidden(path) != "" \
            and check_last_update_date_within_folder(path) is True\
            and check_all_country_available(path) is True:
        return True
    else:
        return False


def copy_order_report_from_intranet():
    from_path = "\\\\10.12.50.3\\data_source\\order_csv"
    to_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
              "Shopee 2016.4.12\\2016.4.23 Data Visualization\\Order"

    # pprint(listdir_not_hidden(from_path))

    # 首先，如果文件夹不为空，说明文件已经开始录入，但是得稍等一下，因为文件没有完全进入到这个文件夹，sleep一下
    # 但是，文件夹不为空，也有可能是昨天的文件没有删除，所以要判断一下
    if check_data_validation(from_path) is True:
        print('Sleep for 5 min for order data unfolded')
        time.sleep(300)

        for folderName, subfolders, filenames in os.walk(from_path):
            # print('The current folder is ' + folderName)

            for filename in filenames:
                if filename.endswith('.csv'):
                    country_name = filename.split('_')[2][:2]
                    # print('File inside ' + folderName + ': ' + filename + ', and country name ' + country_name)
                    file_path = os.path.join(folderName, filename)
                    to_path_sub = os.path.join(to_path, country_name)

                    # 复制到本地文件夹
                    shutil.copy(file_path, to_path_sub)
                    print(filename + ' copied completed.')
    # else:
        # print('order report not downloaded to intranet yet!')
    else:
        return False


def copy_listing_report_from_intranet():
    from_path = "\\\\10.12.50.3\\data_source\\listing_csv"
    to_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
              "Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing"

    # pprint(listdir_not_hidden(from_path))

    # 首先，如果文件夹不为空，说明文件已经开始录入，但是得稍等一下，因为文件没有完全进入到这个文件夹，sleep一下
    # 但是，文件夹不为空，也有可能是昨天的文件没有删除，所以要判断一下
    if check_data_validation(from_path) is True:
        print('Sleep for 5 min for listing data unfolded')
        time.sleep(300)

        for folderName, subfolders, filenames in os.walk(from_path):
            # print('The current folder is ' + folderName)
            for filename in filenames:
                if filename.endswith('.csv'):
                    country_name = filename[:2]
                    # rare_part = filename[-6:]
                    new_file_name = filename[:10] + filename[-6:]
                    # print('File inside ' + folderName + ': ' + filename + ', and country name ' + country_name)
                    # print('New file name ' + new_file_name)
                    file_path = os.path.join(folderName, filename)
                    to_path_sub = os.path.join(to_path, country_name, new_file_name)

                    # 复制到本地文件夹
                    shutil.copy(file_path, to_path_sub)
                    print(new_file_name + ' copied completed.')
    # else:
        # print('listing report not downloaded to intranet yet!')
    else:
        return False


def copy_pricing_report_from_intranet():
    from_path = "\\\\10.12.50.3\\data_source\\pricing_csv"
    to_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
              "Shopee 2016.4.12\\2016.4.23 Data Visualization\\Pricing"

    # pprint(listdir_not_hidden(from_path))

    # 首先，如果文件夹不为空，说明文件已经开始录入，但是得稍等一下，因为文件没有完全进入到这个文件夹，sleep一下
    # 但是，文件夹不为空，也有可能是昨天的文件没有删除，所以要判断一下
    if check_data_validation(from_path) is True:
        print('Sleep for 5 min for pricing data unfolded')
        time.sleep(300)

        for folderName, subfolders, filenames in os.walk(from_path):
            # print('The current folder is ' + folderName)

            for filename in filenames:
                if filename.endswith('.csv'):
                    country_name = filename.split('_')[2][:2]
                    # print('File inside ' + folderName + ': ' + filename + ', and country name ' + country_name)
                    file_path = os.path.join(folderName, filename)
                    to_path_sub = os.path.join(to_path, country_name)

                    # 复制到本地文件夹
                    shutil.copy(file_path, to_path_sub)
                    print(filename + ' copied completed.')
    # else:
        # print('pricing report not downloaded to intranet yet!')
    else:
        return False


def copy_product_view_report_from_intranet():
    from_path = "\\\\10.12.50.3\\data_source\\product_view_csv"
    to_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
              "Shopee 2016.4.12\\2016.4.23 Data Visualization\\ProductView"

    # pprint(listdir_not_hidden(from_path))

    # 首先，如果文件夹不为空，说明文件已经开始录入，但是得稍等一下，因为文件没有完全进入到这个文件夹，sleep一下
    # 但是，文件夹不为空，也有可能是昨天的文件没有删除，所以要判断一下
    if check_data_validation(from_path) is True:
        print('Sleep for 5 min for order data unfolded')
        time.sleep(300)

        for folderName, subfolders, filenames in os.walk(from_path):
            # print('The current folder is ' + folderName)

            for filename in filenames:
                if filename.endswith('.csv'):
                    country_name = filename.split('_')[1][:2]
                    # print('File inside ' + folderName + ': ' + filename + ', and country name ' + country_name)
                    file_path = os.path.join(folderName, filename)
                    to_path_sub = os.path.join(to_path, country_name)

                    # 复制到本地文件夹
                    shutil.copy(file_path, to_path_sub)
                    print(filename + ' copied completed.')
                    return True
    # else:
        # print('product view report not downloaded to intranet yet!')
    else:
        return False


if __name__ == "__main__":
    copy_order_report_from_intranet()
    # copy_listing_report_from_intranet()
    # copy_pricing_report_from_intranet()
    # copy_product_view_report_from_intranet()
    # to_checked_path = "\\\\10.12.50.3\\data_source\\listing_csv"
    # check_last_update_date_within_folder(to_checked_path)
    # check_all_country_available(to_checked_path)
