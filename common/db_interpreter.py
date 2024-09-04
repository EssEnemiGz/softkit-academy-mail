"""
Este archivo se va a basar en funciones para poder interpretar los datos de la base de datos o manejar los mismo.
By: EssEnemiGz

0 = Retorno vacio
200 = Exitoso
500 = Error de la query

Retorno exitoso de datos con .output_data() da una lista con diccionarios
[ {...}, {...} ]
"""

from flask import make_response, jsonify

class db_response():
    def __init__(self, *, response, output, status):
        self.response = response
        self.output = output
        self.status = status
    
    def flask_response(self):
        return self.response
    
    def output_data(self):
        return self.output
    
    def status_code(self):
        return self.status

def return_data(*, query, was_be_empty: int): 
    """
    Retorna el resultado de una query y maneja los errores.

    Informacion esperada: query: consulta de supabase, was_be_empty: int.
    was_be_empty indica que se va a retornar un status de 0 siempre que este argumento sea un 1, si no va a ser un 200 comun.
    El argumento es usado para cuando quieres una consulta que retorne una lista vacia.
    """
    output = None
    try:
        output = query.execute()
        output = output.data
    except Exception as e:
        print(f"\033[1;32m >>> {e}\033[0m")
        err = make_response( jsonify({'status':'Execution of query returned a error.'}) )
        err.status_code = 500

        err_object = db_response(response=err, output=[], status=500)
        return err_object
    
    if len(output) == 0 and not was_be_empty: 
        empty_response = make_response( jsonify( "The query is empty!" ) )
        empty_response.status_code = 200

        empty_object = db_response(response=empty_response, output=output, status=0)
        return empty_object

    response = make_response( jsonify( "Query executed!" ) )
    response.status_code = 200
    object_response = db_response(response=response, output=output, status=200)
    return object_response

def unique_return(*, query, key: str, was_be_empty: int):
    """
    Retorna el resultado de una query y maneja los errores.

    Informacion esperada: query: consulta de supabase, key: str, was_be_empty: int.
    was_be_empty indica que se va a retornar un status de 0 siempre que este argumento sea un 1, si no va a ser un 200 comun.
    El argumento es usado para cuando quieres una consulta que retorne una lista vacia.

    Key es la columna que quieres retornar.
    """
    output = None
    try:
        output = query.execute()
        output = output.data
    except Exception as e:
        print(f"\033[1;32m >>> {e} \033[0m")
        err = make_response( jsonify({'status':'Execution of query returned a error.'}) )
        err.status_code = 500

        err_object = db_response(response=err, output=[], status=500)
        return err_object
    
    if len(output) == 0 and not was_be_empty: 
        empty_response = make_response( jsonify( "The query is empty!" ) )
        empty_response.status_code = 200

        empty_object = db_response(response=empty_response, output=output, status=0)
        return empty_object
    
    if len(output) == 0 and was_be_empty: output = 0 # Siempre que la lista este vacia y el resultado de la query pueda estar vacio
    else: output = output[0].get(key)

    response = make_response( jsonify( "Query executed!" ) )
    response.status_code = 200
    object_response = db_response(response=response, output=output, status=200)
    return object_response

def no_return(*, query):
    """
    Para consultas de escritura, estas no retornan informacion.

    Informacion esperada: query: consulta de supabase.
    """
    try:
        query.execute()
    except Exception as e:
        print(f"\033[1;32m >>> {e}\033[0m")
        err = make_response( jsonify({'status':'Execution of query returned a error.'}) )
        err.status_code = 500

        err_object = db_response(response=err, output=[], status=500)
        return err_object
    
    response = make_response( jsonify( "Query executed!" ) )
    response.status_code = 200
    object_response = db_response(response=response, output=None, status=200)
    return object_response