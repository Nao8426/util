import csv
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import statistics
import torch
import torchvision
from PIL import Image
from torch import nn
from torchvision.transforms import ToTensor
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Dataset(torch.utils.data.Dataset):
    def __init__(self, image_root, df_path, mode=0):
        self.root = image_root
        self.mode = mode
        with open(df_path) as f:
            reader = csv.reader(f)
            l = [row for row in reader]
            for x in zip(*l):
                self.l_T = list(x)

    def __len__(self):
        return len(self.l_T)

    def __getitem__(self, i):
        image = Image.open(self.l_T[i])
        if self.mode == 0:
            image = image.convert('L')
        image = image.resize((125, 125))
        image = ToTensor()(image)

        return image


class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=5, stride=2, padding=0),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),

            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=2, padding=0),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=2, padding=0),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),

            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),

            nn.ConvTranspose2d(in_channels=256, out_channels=128, kernel_size=3, stride=2, padding=0),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),

            nn.ConvTranspose2d(in_channels=128, out_channels=64, kernel_size=3, stride=2, padding=0),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            nn.ConvTranspose2d(in_channels=64, out_channels=32, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),

            nn.ConvTranspose2d(in_channels=32, out_channels=3, kernel_size=5, stride=2, padding=0),
            nn.BatchNorm2d(3),
            nn.Tanh()
        )

    def forward(self, x):
        return self.model(x)


class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=32, kernel_size=5, stride=1, padding=0),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.2, inplace=True),

            nn.MaxPool2d(kernel_size=3, stride=1, padding=0),

            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=5, stride=1, padding=0),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True),

            nn.MaxPool2d(kernel_size=3, stride=1, padding=0),

            nn.Flatten(start_dim=1, end_dim=3),
            nn.Linear(in_features=64*113*113, out_features=64),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Linear(in_features=64, out_features=1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x).squeeze()


class MyLoss():
    def __init__(self):
        self.BCE_loss = nn.BCEWithLogitsLoss()
        self.L1_loss = nn.L1Loss()

    def loss(self, a, b, c, d, alpha=1):
        return self.BCE_loss(a, b)+alpha*self.L1_loss(c, d)


# 損失の履歴をプロット
def plot(loss_G, loss_D, epochs, dirname):
    fig = plt.figure(figsize=(12.8, 4.8))

    ax_G = fig.add_subplot(1, 2, 1)
    ax_G.plot(epochs, loss_G)
    ax_G.set_title('Generator Loss')
    ax_G.set_xlabel('epoch')
    ax_G.set_ylabel('loss')

    ax_D = fig.add_subplot(1, 2, 2)
    ax_D.plot(epochs, loss_D)
    ax_D.set_title('Discriminator Loss')
    ax_D.set_xlabel('epoch')
    ax_D.set_ylabel('loss')
        
    os.makedirs(dirname, exist_ok=True)
    fig.savefig('{}/loss_{}.png'.format(dirname, len(epochs)))


def train(savedir, epochs=100, batch_size=16):
    device = 'cuda'

    model_G, model_D = Generator(), Discriminator()
    model_G, model_D = nn.DataParallel(model_G), nn.DataParallel(model_D)
    model_G, model_D = model_G.to(device), model_D.to(device)

    # Optimizer（最適化アルゴリズム）
    para_G = torch.optim.Adam(model_G.parameters(), lr=0.0002, betas=(0.5, 0.999))
    para_D = torch.optim.Adam(model_D.parameters(), lr=0.0002, betas=(0.5, 0.999))

    # ロス計算のためのラベル変数
    ones = torch.ones(512).to(device)
    zeros = torch.zeros(512).to(device)

    # 損失関数
    myloss = MyLoss()
    loss_f = nn.BCEWithLogitsLoss()

    # エラー推移
    result = {}
    result["log_loss_G"] = []
    result["log_loss_D"] = []

    contour = Dataset('.\\contour', 'contour.csv', 0)
    illust = Dataset('.\\illust', 'illust.csv', 1)

    train_contour = torch.utils.data.DataLoader(contour, batch_size=batch_size)
    train_illust = torch.utils.data.DataLoader(illust, batch_size=batch_size)

    for i in range(epochs):
        print('########## epoch : {}/{} ##########'.format(i+1, epochs))
        log_loss_G, log_loss_D = [], []
        ite = 1
        for contour, illust in zip(train_contour, train_illust):
            contour, illust = contour.to(device), illust.to(device)

            # Generatorに入力
            fake_illust = model_G(contour)
            contour_tensor = contour.detach()
            fake_illust_tensor = fake_illust.detach()

            # Generatorのロス計算
            out = model_D(fake_illust)
            loss_G = myloss.loss(out, ones[:batch_size], fake_illust, illust, 1)
            log_loss_G.append(loss_G.item())

            # 微分計算・重み更新
            para_D.zero_grad()
            para_G.zero_grad()
            loss_G.backward()
            para_G.step()

            # 実画像を真と識別できるようにロスを計算
            real_out = model_D(illust)
            loss_D_real = loss_f(real_out, ones[:batch_size])

            # 偽画像を偽と識別できるようにロスを計算
            fake_out = model_D(fake_illust)
            loss_D_fake = loss_f(fake_out, zeros[:batch_size])

            # 実画像と偽画像のロスを合計
            loss_D = loss_D_real + loss_D_fake
            log_loss_D.append(loss_D.item())

            # 微分計算・重み更新
            para_D.zero_grad()
            para_G.zero_grad()
            loss_D.backward()
            para_D.step()

            if ite % 50 == 0:
                print('iteration : {}'.format(ite))

            ite += 1

        result["log_loss_G"].append(statistics.mean(log_loss_G))
        result["log_loss_D"].append(statistics.mean(log_loss_D))
        print("loss_G =", result["log_loss_G"][-1], ", loss_D =", result["log_loss_D"][-1])

        # 画像を保存
        os.makedirs(savedir, exist_ok=True)
        os.makedirs('{}/input'.format(savedir), exist_ok=True)
        torchvision.utils.save_image(contour_tensor[:batch_size], "{}/epoch_{:03}.png".format(savedir, i+1))
        torchvision.utils.save_image(fake_illust_tensor[:batch_size], "{}/input/epoch_{:03}.png".format(savedir, i+1))

        if (i+1) % 10 == 0:
            x = np.linspace(1, i+1, i+1, dtype='int')
            plot(result['log_loss_G'], result['log_loss_D'], x, savedir)
    
            # ログの保存
            os.makedirs('{}/logs'.format(savedir), exist_ok=True)
            with open('{}/logs/logs_{}.pkl'.format(savedir, i+1), 'wb') as fp:
                pickle.dump(result, fp)


if __name__ == '__main__':
    train('.\\progress', epochs=200, batch_size=16)
    