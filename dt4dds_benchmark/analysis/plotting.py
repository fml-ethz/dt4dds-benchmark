import plotly.graph_objects as go
from plotly.subplots import make_subplots

def standardize_plot(fig):
    fig.update_layout(
        template="simple_white",
        font_family="Inter",
        legend_font_size=28/3,
    )
    fig.update_yaxes(
        minor_ticks="outside", 
        title_font_family="Inter", 
        title_font_size=28/3, 
        tickfont_size=28/3, 
    )
    fig.update_xaxes(
        minor_ticks="outside", 
        title_font_family="Inter", 
        title_font_size=28/3, 
        tickfont_size=28/3, 
    )
    fig.for_each_annotation(lambda a: a.update(
        font_size=28/3,
        font_family="Inter",
    ))
    fig.update_coloraxes(
        colorbar_tickfont=dict(family="Inter", size=28/3),
    )
    return fig


def tiered_bar(df, major, minor, metric, color_by=None, error_upper=None, error_lower=None, facet_row=None, facet_row_spacing=0.05, color_discrete_map=None):
    if facet_row:
        fig = make_subplots(
            rows=len(df[facet_row].unique()), 
            cols=1,
            shared_xaxes=True,
            shared_yaxes=True,
            vertical_spacing=facet_row_spacing,
        )
    else:
        fig = go.Figure()


    plot_dfs = [df.loc[df[facet_row] == row].copy() for row in df[facet_row].unique()] if facet_row else [df.copy()]
    
    for i, plot_df in enumerate(plot_dfs):
        # if color_by is specified, group by that column, else put all in one group
        groups = {None: plot_df}
        if color_by:
            unique_ids = plot_df[color_by].unique()
            groups = {id: plot_df[plot_df[color_by] == id] for id in unique_ids}

        # loop through all groups and add a trace for each
        for name, group in groups.items(): 
            args = {}
            # if error_upper and/or error_lower is specified, add error bars
            if error_upper:
                plot_df['error_upper'] = plot_df[error_upper] - plot_df[metric]
                if error_lower:
                    plot_df['error_lower'] = plot_df[metric] - plot_df[error_lower]
                    args['error_y'] = dict(
                        type='data',
                        symmetric=False,
                        array=plot_df['error_upper'].values,
                        arrayminus=plot_df['error_lower'].values,
                    )
                else:
                    args['error_y'] = dict(
                    type='data',
                    symmetric=True,
                    array=plot_df['error_upper'].values,
                )   
            x_vals_major = group[major].values
            x_vals_minor = group[minor].values
            args.update(
                x = [x_vals_major, x_vals_minor],
                y = group[metric].values,
                name = name,
            )
            if color_discrete_map:
                args['marker'] = dict(color=color_discrete_map[name])
            if facet_row: 
                fig.add_trace(go.Bar(**args), row=i+1, col=1)
            else:
                fig.add_trace(go.Bar(**args))
    return fig