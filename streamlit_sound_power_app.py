import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import cmath
from scipy import integrate
from scipy.special import jv, yv, j1

# Define the app title and description
st.title("My Streamlit App")
st.write("This is a simple app to demonstrate the use of Streamlit.")

# Add some interactive widgets
number = st.number_input("Enter a number", value=0)
if st.button('Submit'):
    st.write(f"You entered: {number}")

# 定义一个变量f0，其值为2.25乘以10的6次方，代表频率
f0 = 2.25e6
# 定义一个变量c0，其值为1500.0，代表声速
c0 = 1500.0
# 定义一个变量u，其值为1.0乘以10的3次方，代表质点速度
u = 1.0e3
# 定义一个变量p，其值为1.0乘以10的3次方，代表声压
p = 1.0e3
# 计算角频率w，公式为2乘以π乘以频率f0
w = 2 * math.pi * f0
# 计算波长lamd，公式为声速c0除以频率f0
lamd = c0 / f0
# 计算波数k，公式为2乘以π除以波长lamd
k = 2 * math.pi / lamd

L = lamd / 4

# 将 F、r、a 设为可输入的参数
F = st.number_input("Enter the value of F", value=5e-3)
r = st.number_input("Enter the value of r", value=5e-3)
a = st.number_input("Enter the value of a", value=10e-3)


def Jf(a, xita):
    tmp = 2 * j1(k * a * math.sin(xita))
    ret = tmp / (k * a * math.sin(xita))
    return ret


def SoundPower(r, a, xita, t):
    t1 = w * p * u * (a ** 2) / (2 * r)
    t2 = Jf(a, xita)
    t3 = cmath.exp(complex(0, 1) * (w * t - k * r))
    return np.absolute(t1 * t2 * t3)


xita = np.arange(-np.pi / 2, np.pi / 2, 0.01)
y = np.zeros(len(xita))
for i in np.arange(0, len(xita)):
    y[i] = SoundPower(r, a, xita[i], c0 / f0)

x = xita
fig1, ax1 = plt.subplots()
ax1.plot(x, y)
ax1.set_xlabel('Angle (radians)')
ax1.set_ylabel('Sound Power')
ax1.set_title('Sound Power vs Angle')
st.pyplot(fig1)


def Direction(a, angle):
    ret = Jf(a, angle)
    return np.absolute(ret)


t = 3
angle = np.arange(-np.pi / 2, np.pi / 2, 0.01)
y = np.zeros(len(angle))
for i in np.arange(0, len(angle)):
    y[i] = Jf(t / k, angle[i])

x = angle
fig2, ax2 = plt.subplots()
ax2.plot(x, y)
ax2.set_xlabel('Angle (radians)')
ax2.set_ylabel('Directional Factor')
ax2.set_title('Directional Factor vs Angle')
st.pyplot(fig2)
    