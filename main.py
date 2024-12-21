import sys
import codecs
from pathlib import Path
from pex import toml
from sly import Lexer, Parser


class HighLexer(Lexer):
    tokens = {
        NAME, NUMBER, POINTER, EQ, DEFINE, SEMICOLON, LPAREN, RPAREN, LDICT, RDICT
    }

    # Приказано игнорировать
    ignore_whitespaces = r'[ \t]'
    ignore_newline = r'[\r\n]+'
    # ignore_comment = r'\#.*'
    # NEWLINE = r'[\r\n]+'

    # Основные операции
    EQ = r':='          # Присвоение
    POINTER = r'\$'     # Вычисление константы на этапе трансляции

    # Скобки
    DEFINE = 'def'
    SEMICOLON = r';'
    LPAREN = r'\['
    RPAREN = r'\]'
    LDICT = r'begin'
    RDICT = r'end'

    # Основные данные
    NUMBER = r'\d+'
    NAME = r'[a-zA-Z][a-zA-Z0-9]*'

    # Специальные случаи
    # STRING = r'\" [\w\dа-яА-Я_\-\.\,\s]+ [\w\dа-яА-Я_\-\.\,\s]* \"'

    # Предобработка токена
    def NUMBER(self, t):
        t.value = int(t.value)  # Convert to a numeric value
        return t

    # Трекинг линий
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print('Строка %d: неожиданный синтаксис %r' % (self.lineno, t.value[0]))
        self.index += 1


class HighParser(Parser):
    tokens = HighLexer.tokens   # Получение токенов из Lexer

    def __init__(self):
        self.vars = {}

    @_('statement SEMICOLON statements')
    def statements(self, p):
        return [p.statement] + p.statements

    @_('statement SEMICOLON')
    def statements(self, p):
        return [p.statement]

    @_('DEFINE NAME EQ value')
    def statement(self, p):
        self.vars[p.NAME] = p.value

    @_('POINTER LPAREN NAME RPAREN')
    def value(self, p):
        try:
            return self.vars[p.NAME]
        except LookupError:
            print(f'Undefined name {p.NAME!r}')
            return 0

    @_('LDICT list_assign RDICT')
    def value(self, p):
        d = {}
        d.update(p.list_assign)
        return d

    # assign list_assign
    @_('assign list_assign')
    def list_assign(self, p):
        d = {}
        d.update(p.assign)
        d.update(p.list_assign)
        return d

    @_('')
    def list_assign(self, p):
        return {}

    # assign;
    @_('NAME EQ list_value SEMICOLON')
    def assign(self, p):
        d = {}
        d[p.NAME] = p.list_value
        return d

    # value list_value
    @_('value list_value')
    def list_value(self, p):
        if (isinstance(p.list_value, list)):
            if (len(p.list_value) != 0):
                return [p.value] + p.list_value
            return p.value
        return [p.value] + [p.list_value]

    @_('')
    def list_value(self, p):
        return []

    # Конкретные конструкции для значений
    @_('NUMBER')
    def value(self, p):
        return p.NUMBER

    def error(self, p):
        if p is None:
            print('Ошибка: неожиданный конец входных данных')
        else:
            print(f'Строка {p.lineno}: неожиданный токен "{p.value}"')
        return 1

    # @_('STRING')
    # def value(self, p):
    #     return p.STRING
    #
    # # Правило для входных данных
    # @_('statement statements')
    # def statements(self, p):
    #     p.statement
    #     p.statements
    #
    # # Определение конкретных утверждений
    # @_('DEFINE NAME ASSIGN value SEMICOLON')
    # def statement(self, p):
    #     # Обработка определения
    #     self.vars[p.NAME] = p.value
    #
    # @_('POINTER LPAREN NAME RPAREN')
    # def value(self, p):
    #     try:
    #         return self.vars.get(p.NAME, 0)  # Извлечение значения по указателю
    #     except LookupError:
    #         print(f'Undefined name {p.NAME!r}')
    #         return 0

def create_toml(data):
    toml_string = toml.dumps(data)
    with open('result.toml', 'w') as f:
        f.write(toml_string)
        print('Файл успешно создан!')

def main(argument):
    file_path = Path(argument)

    if not Path.exists(Path(argument)):
        print('Error when attempting to load the file.')
        return 1
    else:
        file = codecs.open(file_path, 'r', 'utf-8')
        data = file.read()

        lexer = HighLexer()
        # for token in lexer.tokenize(data):
        #     print(token)
        parser = HighParser()

        try:
            result = parser.parse(lexer.tokenize(data))
            # print(parser.vars)
            create_toml(parser.vars)
            return parser.vars
        except Exception as e:
            print(f'Непредвиденная ошибка при парсинге: {e}')
            return




if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: program <file_path>")
        sys.exit(1)

    argument = sys.argv[1]
    main(argument)