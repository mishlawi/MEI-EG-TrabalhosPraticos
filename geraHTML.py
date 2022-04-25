def writeInFile(string):
    f = open("index.html", "w", encoding="utf-8")
    f.write(string)
    f.close
    
def geraRel(data): 
    string = '''
<!DOCTYPE html>
<html>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: Arial;
            margin: 0;
        }
        .header {
            padding: 5px;
            text-align: center;
            background: #1a97bc;
            color: white;
            font-size: 15px;
        }
        /* Create two equal columns that floats next to each other */
        .column {
            float: left;
            width: 50%;
            padding: 10px;
            height: 300px; /* Should be removed. Only for demonstration */
        }

        /* Clear floats after the columns */
        .row:after {
            content: "";
            display: table;
            clear: both;
        }

        table, th, td {
            border: 1px solid black;
            width: 100px;
            height: 50px;
        }
      </style>
    <head>
        <title>EG - TP2</title>
        <meta charset="UTF-8"/>
    </head>
    <body>
        <div class="header">
            <h1> 
                <b>Engenharia Gramatical</b>
                <br>
                Relatório 
            </h1>
        </div>
        <p><h3><b> Realizado por: </b></h3></p>
            Angélica Cunha <i>PG47024</i>
            <br>
            Duarte Oliveira <i>PG47157</i>
            <br> 
            Tiago Barata <i>PG47695</i>
        <hr>''' + f'''
        <h2>1. Variáveis</h2>
            <ul>
                <li><b>Variáveis redeclaradas: </b>{data["vars"]["RED"]} (#TOTAL: {len(data["vars"]["RED"])})</li>
                <li><b>Variáveis não-declaradas: </b>{data["vars"]["ND"]} (#TOTAL: {len(data["vars"]["ND"])})</li>
                <li><b>Variáveis usadas, mas não inicializadas: </b>{data["vars"]["UNI"]} (#TOTAL: {len(data["vars"]["UNI"])})</li>
                <li><b>Variáveis declaradas, mas nunca mencionadas: </b>{data["vars"]["DN"]} (#TOTAL: {len(data["vars"]["DN"])})</li>
            </ul>
        <h2>2. Variáveis declaradas vs. Dados estruturados</h2>
            <table>
                <tr>
                    <th rowspan="2"><b>Variáveis</b></th>
                    <th colspan="5"><b>Estruturas</b></th>
                </tr>
                <tr>
                    <td><b>Dicionários</b></th>
                    <td><b>Listas</b></th>
                    <td><b>Tuplos</b></th>
                    <td><b>Conjuntos</b></th>
                    <td><b>Total</b></th>
                </tr>
                <tr>
                    <td>{data["#varsDec"]}</td>
                    <td>{data["#estruturas"]["dicts"]}</td>
                    <td>{data["#estruturas"]["listas"]}</td>
                    <td>{data["#estruturas"]["tuplos"]}</td>
                    <td>{data["#estruturas"]["conjuntos"]}</td>
                    <td>{data["#estruturas"]["conjuntos"]+data["#estruturas"]["tuplos"]+data["#estruturas"]["listas"]+data["#estruturas"]["dicts"]}</td>
                </tr>
            </table>
        <h2>3. Instruções</h2>
            <table>
                <tr>
                    <th><b>Atribuições</b></th>
                    <th><b>Leitura e Escrita</b></th>
                    <th><b>Condicionais</b></th>
                    <th><b>Ciclos</b></th>
                    <th><b>Total</b></th>
                </tr>
                <tr>
                    <td>{data["#inst"]["atribuicao"]}</td>
                    <td>{data["#inst"]["rw"]}</td>
                    <td>{data["#inst"]["cond"]}</td>
                    <td>{data["#inst"]["ciclo"]}</td>
                    <td>{data["#inst"]["ciclo"]+data["#inst"]["cond"]+data["#inst"]["rw"]+data["#inst"]["atribuicao"]}</td>
                </tr>
            </table>
        <h2>4. Estruturas de controlo aninhadas</h2>
            <table>
                <tr>
                    <th><b>Mesmo tipo</b></th>
                    <th><b>Tipos diferentes</b></th>
                </tr>
                <tr>
                    <td>{data["#estruturasAninh"]["mm"]}</td>
                    <td>{data["#estruturasAninh"]["dif"]}</td>
                </tr>
            </table>
        <h2>5. Ifs aninhados</h2>
            <div class="row">
                <div class="column">
                    <h2>Antes</h2>'''
    for elem in data["estruturasAninhadas"].keys():
        string += "\t\t\t\t\t<p>" + elem + "</p>\n"
    string += '''
                </div>
                <div class="column">
                    <h2>Depois</h2>'''
    for elem in data["estruturasAninhadas"].keys():
        string += "\t\t\t\t\t<p>" + data["estruturasAninhadas"][elem] + "</p>\n"
    string += '''
                </div>
            </div>
    </body>
</html>'''

    writeInFile(string)
       