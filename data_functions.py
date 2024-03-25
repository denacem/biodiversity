def prepare_pdf_data(pdf_data):
    split_columns = pdf_data['occupation/transformation'].str.split(',', n=3, expand=True)
    pdf_data['occupation'] = split_columns[1].str.strip()
    pdf_data['country_code'] = split_columns[2].str.strip()

    return pdf_data