import pandas as pd
import matplotlib.pyplot as plt

plt.switch_backend('agg')

def visual(true, preds=None, date_data=None, title='', name='./pic/test.png'):
    """
    Results visualization
    """
    metric = title.split(" ")[-1]

    _, ax = plt.subplots()
    sec_ax = ax.secondary_xaxis('bottom')

    if preds is not None:
        color = 'orange'
        if (preds[-1] >= preds[len(true)]):
            color = 'blue'
        else:
            color = 'red'

        ax.plot(preds, label='Prediction', linewidth=2, color=color)
    ax.plot(true, label='GroundTruth', linewidth=2, color='#3C3C3C')

    ax.set_ylabel(metric)
    if date_data is not None:
        date_data = pd.to_datetime(date_data)

        hour_labels = [dt.strftime('%H') for dt in date_data]
        day_month_labels = [dt.strftime('%b/%d') for dt in date_data]

        ax.set_xticks(range(0, len(hour_labels), 6))
        ax.set_xticklabels(hour_labels[::6])

        sec_ax.set_xticks(range(0, len(day_month_labels), 24))
        sec_ax.set_xticklabels(day_month_labels[::24])
        sec_ax.tick_params(axis='x', pad=15)
        
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_title(title)
    ax.legend()

    plt.tight_layout()
    plt.savefig(name, bbox_inches='tight')