            "남성 인구: %{customdata:,}명"
            "<extra></extra>"
        ),
        customdata=male_population
    )
)

# 여성 인구는 양수로 설정하여 오른쪽에 그립니다.
fig.add_trace(
    go.Bar(
        y=ages,
        x=female_population,
        name="여성",
        orientation="h",
        marker_color="#E8B86D",
        hovertemplate=(
            "나이: %{y}<br>"
            "여성 인구: %{x:,}명"
            "<extra></extra>"
        )
    )
)

# 가로축 눈금은 음수인 남성 인구도 양수처럼 보이게 표시합니다.
max_population = max(
    float(male_population.max()),
    float(female_population.max()),
    1
)
axis_limit = max(1, int(np.ceil(max_population / 100) * 100))
tick_step = max(1, axis_limit // 5)
tick_values = list(range(-axis_limit, axis_limit + 1, tick_step))
tick_text = [f"{abs(value):,}" for value in tick_values]

fig.update_layout(
    title={
        "text": f"{selected_dong} 연령별 인구 피라미드",
        "x": 0.5,
        "xanchor": "center"
    },
    barmode="overlay",
    bargap=0.12,
    height=1000,
    paper_bgcolor="#FFF9F2",
    plot_bgcolor="#FFF9F2",
    font=dict(family="Arial, sans-serif", size=12, color="#5C4638"),
    legend=dict(
        title="성별",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    margin=dict(l=80, r=40, t=100, b=70),
    xaxis=dict(
        title="인구수 (명)",
        range=[-axis_limit, axis_limit],
        tickmode="array",
        tickvals=tick_values,
        ticktext=tick_text,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="#BCA18A",
        gridcolor="#EADFD4"
    ),
    yaxis=dict(
        title="나이",
        type="category",
        # 나이 라벨을 0세부터 100세 이상까지 직접 고정합니다.
        # Plotly 범주축에서는 이 순서가 아래에서 위로 표시됩니다.
        categoryorder="array",
        categoryarray=ages,
        tickmode="array",
        tickvals=ages,
        ticktext=ages,
        tickfont=dict(size=10),
        gridcolor="#F1E6DC"
    )
)

st.plotly_chart(fig, use_container_width=True)

# 그래프 아래에 아이와 어르신 인구를 비교한 자동 설명을 표시합니다.
st.markdown(
    f'<div class="summary-note">💬 {population_summary}</div>',
    unsafe_allow_html=True
)

st.caption(
    "※ 남성 인구는 그래프에서 왼쪽으로 표시하기 위해 음수로 변환했습니다. "
    "평균연령 계산에서 100세 이상은 100세로 간주했습니다."
)


# ------------------------------------------
# 8. 나이별 인구 데이터 표
# ------------------------------------------
with st.expander("📋 나이별 남녀 인구 표 보기"):
    population_table = pd.DataFrame({
        "나이": ages,
        "남성 인구": male_population.astype(int),
        "여성 인구": female_population.astype(int),
        "전체 인구": age_population.astype(int)
    })

    st.dataframe(
        population_table,
        use_container_width=True,
        hide_index=True
    )

st.divider()
st.caption("자료: 제공된 읍·면·동 연도별 성별 인구 데이터")
