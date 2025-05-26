from models import User, Snippet, Publicacion, Comentario
import sqlalchemy.orm as _orm
from sqlalchemy import func 
import schemas.user as _user

from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_informe(db: _orm.Session, user: _user.User):

    cantidad_usuarios = db.query(func.count(User.Userid)).scalar()
    cantidad_snippets = db.query(func.count(Snippet.Snippetid)).scalar()
    cantidad_publicaciones = db.query(func.count(Publicacion.Publicacionid)).scalar()
    cantidad_comentarios = db.query(func.count(Comentario.ComentarioId)).scalar()
    cantidad_usuarios_activos = db.query(func.count(User.Userid)).filter(User.activo == True).scalar()
    cantidad_snippets_aprobados = db.query(func.count(Snippet.Snippetid)).filter(Snippet.activo == True).scalar()

    stats = {
        "total_usuarios": cantidad_usuarios,
        "total_snippets": cantidad_snippets,
        "total_publicaciones": cantidad_publicaciones,
        "total_comentarios": cantidad_comentarios,
        "snippets_aprobados": cantidad_snippets_aprobados,
        "usuarios_activos": cantidad_usuarios_activos,
    }

    barras = client.responses.create(
        model="gpt-4.1-nano",
        input=f"""
            Actúa como un analista de datos experto y objetivo. A continuación, te proporcionaré datos destinados a una gráfica de barras (o la descripción de una). Tu tarea es realizar un análisis conciso y altamente profesional de la información que esta gráfica representaría, destacando:

            1.  **Comparaciones Clave:** Las diferencias más notables en magnitud entre las categorías/barras.
            2.  **Valores Dominantes/Mínimos:** Qué categorías destacan por tener los valores más altos o más bajos.
            3.  **Patrones o Distribución:** Cualquier patrón visible en la distribución de los valores a través de las categorías.
            4.  **Insights Relevantes:** Conclusiones o implicaciones importantes que se puedan inferir de las comparaciones visuales que ofrecería la gráfica.

            Presenta tus hallazgos en **párrafos cortos**, de manera estructurada, clara y con un lenguaje formal y preciso, como si estuvieras explicando la composición del total a una audiencia ejecutiva. Evita especulaciones no fundamentadas en los datos proporcionados.
            
            **No utilices formato markdown para el énfasis (por ejemplo, no uses asteriscos para negritas como **texto**); presenta todo el análisis en texto plano.** Evita especulaciones sobre los datos.

            ESTADISTICAS: {stats}

        """
    )

    torta = client.responses.create(
        model="gpt-4.1-nano",
        input=f"""
            Actúa como un analista de datos experto y objetivo. A continuación, te proporcionaré datos destinados a una gráfica de torta/pastel (o la descripción de una). 
            Tu tarea es realizar un análisis conciso y altamente profesional de la información que esta gráfica representaría, enfocándote en:

            1.  **Comparaciones Clave:** Diferencias notables de magnitud entre categorías/barras.
            2.  **Valores Dominantes/Mínimos:** Categorías con valores más altos o bajos.
            3.  **Patrones o Distribución:** Patrones visibles en los valores entre categorías.
            4.  **Insights Relevantes:** Conclusiones importantes de las comparaciones visuales.

            Presenta los hallazgos en **cuatro párrafos cortos**, de forma estructurada, clara, formal y precisa para ejecutivos. Sin especulaciones sobre los datos. 
            
            **No utilices formato markdown para el énfasis (por ejemplo, no uses asteriscos para negritas como **texto**); presenta todo el análisis en texto plano.** Evita especulaciones 
            sobre los datos.

            ESTADISTICAS: {stats}

        """
    )


    return {
        "total_usuarios": cantidad_usuarios,
        "total_snippets": cantidad_snippets,
        "total_publicaciones": cantidad_publicaciones,
        "total_comentarios": cantidad_comentarios,
        "snippets_aprobados": cantidad_snippets_aprobados,
        "usuarios_activos": cantidad_usuarios_activos,
        "barras": barras.output_text,
        "torta": torta.output_text
    }
