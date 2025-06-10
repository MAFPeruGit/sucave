from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # puedes reemplazar "*" por el dominio de tu frontend si deseas limitarlo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def fill_value_corrected(value, length, fill_side):
    if pd.isnull(value) or value == 'null':
        return ' ' * length
    value_str = str(value)
    if fill_side == 'left':
        return value_str.zfill(length) if len(value_str) < length else value_str
    elif fill_side == 'right':
        return value_str.ljust(length, '0') if len(value_str) < length else value_str
    elif fill_side == 'none':
        return value_str
    return value_str

def add_spaces_before_correlativo(correlativo):
    if correlativo < 10:
        return ' ' * 5
    elif correlativo < 100:
        return ' ' * 4
    elif correlativo < 1000:
        return ' ' * 3
    return ''

def convert_row_to_format_corrected(excel_row, row_index, specs):
    formatted_values = []
    for col_index, (length, fill_side) in enumerate(specs):
        formatted_values.append(fill_value_corrected(excel_row[col_index], length, fill_side))
    concatenated_values = ''.join(formatted_values)
    correlativo_spaces = add_spaces_before_correlativo(row_index)
    return f"{correlativo_spaces}{row_index:01d}{concatenated_values}"

def generate_header(mes_reporte):
    valor_permanente1 = '02240100185'
    fecha_reporte = f"2025{mes_reporte:02d}30"
    valor_permanente2 = '0004000'
    meses_codigos = {
        1: '31000000000', 2: '41000000000', 3: '51000000000',
        4: '61000000000', 5: '71000000000', 6: '81000000000',
        7: '91000000000', 8: '10100000000', 9: '11100000000',
        10: '12100000000', 11: '13100000000', 12: '14100000000'
    }
    depende_del_mes = meses_codigos[mes_reporte]
    return f"{valor_permanente1}{fecha_reporte}{valor_permanente2}{depende_del_mes}"

def generate_final_row(sheet_data):
    final_row = " 50000"
    sum_columns_indices = [6] + [i for i in range(9, 31) if i != 13]
    for index in range(len(sheet_data.columns)):
        if index == 0:
            final_row += " " * 3
        elif index == 1:
            final_row += " " * 4
        elif index == 2:
            final_row += " " * 3
        elif index == 3:
            final_row += " " * 6
        elif index == 4:
            final_row += " " * 4
        elif index == 5:
            final_row += " " * 3
        elif index == 6:
            col_sum = sheet_data.iloc[:, index].sum()
            final_row += f"{str(int(col_sum)).zfill(6)}"
        elif index in [7, 8]:
            final_row += " " * 1
        elif index == 13:
            final_row += " " * 3
        elif index == 31:
            valores = sheet_data.iloc[:, index]
            suma = valores.sum()
            cantidad = valores.count()
            promedio = round(suma / cantidad) if cantidad > 0 else 0
            final_row += f"{str(promedio).zfill(6)}"
        elif index in sum_columns_indices:
            col_sum = sheet_data.iloc[:, index].sum()
            final_row += f"{str(int(col_sum)).zfill(6)}"
        else:
            final_row += " " * 6
    return final_row

column_specs_latest = [
    (3, 'left'), (4, 'left'), (3, 'left'), (4, 'left'), (4, 'left'), (3, 'left'), (6, 'left'), (1, 'none'), (1, 'none'),
    (6, 'left'), (6, 'left'), (6, 'left'), (6, 'left'), (3, 'left'), (6, 'left'), (6, 'left'), (6, 'left'), (6, 'left'),
    (6, 'left'), (6, 'left'), (6, 'left'), (6, 'left'), (6, 'left'), (6, 'left'), (6, 'left'), (6, 'left'), (6, 'left'),
    (6, 'left'), (6, 'left'), (6, 'left'), (6, 'left'), (6, 'left')
]

@app.post("/generar-archivo")
def generar_archivo(file: UploadFile, mes: int = Form(...)):
    df = pd.read_excel(file.file, header=None).iloc[1:].dropna(how='all')
    header = generate_header(mes)
    formatted_lines = [convert_row_to_format_corrected(df.iloc[i], i + 1, column_specs_latest) for i in range(len(df))]
    final_row = generate_final_row(df)

    with NamedTemporaryFile(delete=False, mode='w', newline='\r\n', suffix='.224') as tmp:
        tmp.write(header + '\n')
        for line in formatted_lines:
            tmp.write(line.rstrip() + '\n')
        tmp.write(final_row + '\n')
        temp_path = tmp.name

    return FileResponse(temp_path, filename=f"0125{mes:02d}31.224", media_type='text/plain')
