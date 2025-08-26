from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, condecimal
from enum import Enum
from decimal import Decimal, getcontext
import math

# Increase precision
getcontext().prec = 28

app = FastAPI(title="Calculator API with UI", version="2.0.0")

# Serve static files (for background image)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----- Models -----
class Op(str, Enum):
    add = "add"
    sub = "sub"
    mul = "mul"
    div = "div"
    pow = "pow"
    sqrt = "sqrt"

class CalcIn(BaseModel):
    a: condecimal(max_digits=30, decimal_places=10)
    b: condecimal(max_digits=30, decimal_places=10) | None = None
    op: Op

# ----- Operation symbols -----
OP_SYMBOLS = {
    Op.add: "+",
    Op.sub: "−",
    Op.mul: "×",
    Op.div: "÷",
    Op.pow: "^",
    Op.sqrt: "√",
}

# ----- Core logic -----
def compute(a: Decimal, b: Decimal | None, op: Op) -> Decimal:
    if op == Op.add:
        return a + b
    if op == Op.sub:
        return a - b
    if op == Op.mul:
        return a * b
    if op == Op.div:
        if b == 0:
            raise HTTPException(status_code=400, detail="Division by zero is not allowed.")
        return a / b
    if op == Op.pow:
        return a ** b
    if op == Op.sqrt:
        if a < 0:
            raise HTTPException(status_code=400, detail="Square root of negative number is not allowed.")
        return Decimal(math.sqrt(float(a)))
    raise HTTPException(status_code=400, detail="Unknown operation.")

# ----- HTML Page -----
@app.get("/", response_class=HTMLResponse, tags=["ui"])
def home(request: Request):
    return """
    <html>
    <head>
        <title>FastAPI Calculator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background-image: url('/static/bg.jpg');
                background-size: cover;
                background-position: center;
                color: white;
            }
            .container {
                background: rgba(0, 0, 0, 0.6);
                padding: 20px;
                border-radius: 15px;
                display: inline-block;
            }
            input, select, button {
                padding: 10px;
                margin: 5px;
                font-size: 16px;
                border-radius: 8px;
                border: none;
            }
            button {
                cursor: pointer;
                background: #4CAF50;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧮 Calculator</h1>
            <form action="/calc_ui" method="get">
                <input type="number" step="any" name="a" placeholder="Enter number A" required>
                <select name="op">
                    <option value="add">+</option>
                    <option value="sub">−</option>
                    <option value="mul">×</option>
                    <option value="div">÷</option>
                    <option value="pow">^</option>
                    <option value="sqrt">√</option>
                </select>
                <input type="number" step="any" name="b" placeholder="Enter number B">
                <br>
                <button type="submit">Calculate</button>
            </form>
        </div>
    </body>
    </html>
    """

# ----- Calculator UI endpoint -----
@app.get("/calc_ui", response_class=HTMLResponse, tags=["ui"])
def calc_ui(a: float, op: Op, b: float | None = None):
    a_dec = Decimal(a)
    b_dec = Decimal(b) if b is not None else None
    result = compute(a_dec, b_dec, op)
    symbol = OP_SYMBOLS[op]

    if op == Op.sqrt:
        expression = f"{symbol}({a_dec}) = {result}"
    else:
        expression = f"{a_dec} {symbol} {b_dec} = {result}"

    return f"""
    <html>
    <body style="text-align:center; background:url('/static/bg5.jpg'); background-size:cover; color:white; padding:50px;">
        <h2>Result</h2>
        <h3>{expression}</h3>
        <a href="/"> Back</a>
    </body>
    </html>
    """
