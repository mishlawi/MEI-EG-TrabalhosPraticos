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
        hr { background-color: #1a97bc; height: 1px; border: 0; }
        body {
            font-family: Arial;
            margin: 0;
        }
        code {
            display: block;
            white-space: pre-wrap;  
            text-align: initial;
        }
        .header {
            padding: 5px;
            text-align: center;
            background: #1a97bc;
            color: white;
            font-size: 15px;
        }
        .autores{
            padding: 20px;
        }

        .container{
            padding: 20px;
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

        table, td, th {  
          border: 1px solid #343738;
          text-align: center;
        }

        table {
          margin-left: 70px;
          margin-right: 70px;
          border-collapse: collapse;
          width: 90%;
        }
        th {
            background: #0099c0;
            color: white;
        }
        th, td {
          padding: 15px;
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
        <div class="autores">
            <p><h3><b> Realizado por: </b></h3></p>
                Angélica Cunha <i>PG47024</i>
                <br>
                Duarte Oliveira <i>PG47157</i>
                <br> 
                Tiago Barata <i>PG47695</i>
        </div>
        <hr>''' + f'''
        <div class="container">
            <h3>1. Variáveis</h3>
                <ul style="list-style-type:none">
                    <li><b >Variáveis do programa: </b> {len(data["vars"]["VARS"])} 
                            &nbsp;&nbsp;{data["vars"]["VARS"]} </li>
                    <li><b>Variáveis redeclaradas: </b> {len(data["vars"]["RED"])} 
                             &nbsp;&nbsp;{data["vars"]["RED"]} </li>
                    <li><b>Variáveis não-declaradas: </b> {len(data["vars"]["ND"])} 
                             &nbsp;&nbsp;{data["vars"]["ND"]} </li>
                    <li><b>Variáveis usadas, mas não inicializadas: </b> {len(data["vars"]["UNI"])} 
                             &nbsp;&nbsp; {data["vars"]["UNI"]}</li>
                    <li><b>Variáveis declaradas, mas nunca mencionadas: </b>{len(data["vars"]["DN"])} 
                             &nbsp;&nbsp; {data["vars"]["DN"]} </li>
                </ul>
            <h3>2. Variáveis declaradas vs. Dados estruturados</h3>
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
            <h3>3. Instruções</h3>
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
            <h3>4. Estruturas de controlo aninhadas</h3>
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
            <h3>5. Ifs aninhados</h3>
                <table>
                    <tr>
                        <th><b>Antes</b></th>
                        <th><b>Depois</b></th>
                    </tr>
                    '''
    for elem in data["estruturasAninhadas"].keys():
        string += "<tr><td>\n\t\t\t\t\t<code>" + elem + "\t\t\t\t\t</code>\n</td>"
        string += "<td>\n\t\t\t\t\t<code>" + data["estruturasAninhadas"][elem] + "\t\t\t\t\t</code>\n</td></tr>"
    string += '''
                    </tr>
                </table>
                 </div>
             </div>
        </div>
    </body>
</html>'''

    writeInFile(string)
       