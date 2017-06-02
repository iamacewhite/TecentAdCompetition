import pandas as pd
import numpy as np
import os

def ensemble(mode, calc):
    for model in os.listdir('models'):
        if not os.path.exists('outputs/output_{}_{}'.format(mode, model)):
            os.system('../libffm/ffm-predict ffm_{}.txt models/{} outputs/output_{}_{}'.format(mode, model, mode, model))

    outputs = []
    for output in os.listdir('outputs'):
        with open('outputs/output_{}_{}'.format(mode, model)) as f:
            content = [item.strip() for item in f.readlines()]
        outputs.append(map(float, content))

    if calc == 'mean':
        outputs = np.array(outputs)
        print len(outputs)
        output = np.mean(outputs, axis=0)
        print len(output)
        write_to_file(mode, output, calc)

    elif calc == 'vote':
        outputs = zip(*outputs)
        output = []
        for row in outputs:
            output.append(int(len(filter(lambda x: x>=0.5, row))>len(row)/2))
        write_to_file(mode, output, calc)

    elif calc == 'mean after vote':
        outputs = zip(*outputs)
        output = []
        for row in outputs:
            larger = filter(lambda x: x>=0.5, row)
            smaller = filter(lambda x: x<0.5, row)
            if len(larger) > len(smaller):
                output.append(np.mean(larger))
            else:
                output.append(np.mean(smaller))
        write_to_file(mode, output, calc)

def write_to_file(mode, output, calc):
    if mode == 'validate':
        with open('output', 'w+') as f:
            for num in output:
                f.write(str(num)+'\n')
            print "final ensemble {}:".format(calc)
        os.system('python check_loss.py')
    else:
        with open('submission', 'w+') as f:
            for num in output:
                f.write(str(num)+'\n')


if __name__ == "__main__":
    #ensemble('validate', 'mean')
    #ensemble('validate', 'vote')
    ensemble('validate', 'mean after vote')
    ensemble('test', 'mean after vote')
