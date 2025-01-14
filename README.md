# yobot_remix

yobot魔改版，支持新版公会战。<br>

使用gensokyo代替gocq，感谢gensokyo的适配<br>
现已支持qq频道指令。<br>

## 转移至频道的食用方法
1.申请qq频道bot，拿到AppID<br>
2.config中增加AppID<br>
3.运行gensokyo，详情请见[gensokyo](https://github.com/Hoshinonyaruko/Gensokyo)<br>
4.填写yobot反代地址<br>
5.在qq开放平台中添加指令，在yobot指令前加/，例如/状态，/报刀<br>

## 指令表
> 大部分和原版yobot相同，只标出和原版yobot不同的命令

|       指令        |                             说明                             |
| :---------------: | :----------------------------------------------------------: |
|申请出刀 [指定boss] [是否为补偿] [@某人]|如：**申请出刀 1** 或 **申请出刀 2b**（b为指定补偿）<br>开始挑战boss，进入**出刀状态**<br>必须指定boss，可以不指定补偿，当完整刀使用完后自动使用补偿<br>（新增申请出刀方式，发送 **进x** 即可，x为指定boss）|
|取消(出刀/申请) [@某人]/[all]|**出刀状态**下可用<br>退出出刀状态。@某人为取消指定成员的出刀申请，加all则取消所有人的出刀申请|
|报伤害 ?s?w [@某人]|**出刀状态**下可用<br>如：**报伤害 2s200w**<br>申请出刀后暂停报伤害，例子意为剩2秒打了200w伤害。可@某人为其报伤害|
|报刀 [-指定boss] [具体伤害] [是否是补偿] [@某人] [昨日] [:留言]|例1：**报刀 -1 100w** <br> 例2：**报刀 100w@xxx** <br> 例3：**报刀 -1 100w b** （b代表指定补偿）<br>对boss造成伤害但未击败时用，记录伤害，并退出**出刀状态**。<br>**指定boss需要在前面加个-（横杠）**，若在**出刀状态**，可以不指定boss<br>一般情况下不需要指定为补偿，会自动选择<br>如果有at则为代报，有冒号则为留言<br>如果有“昨日”则将记录添加到前一天|
|尾刀 [指定boss] [是否是补偿] [@某人] [昨日] [:留言]|同上，不需要具体伤害，指定boss时前面不需要加-（横杠）|
|状态|显示所有boss的当前状态，且可看到当前正在挑战的成员、报伤害、挂树情况|
|挂树|**出刀状态**下可用|
|手动添加群记录|修复多CQ适配（修复网页催刀报刀不在群里通知）|
> 关于指定补偿问题，建议普通公会直接无视指定补偿这个功能，可出刀总数是固定的，不指定也不会有任何影响。<br>
> 有指挥的公会才需要严格遵守。<br>
> 指定补偿时不止可以用b，还可以用 (补偿/补/b/bc)<br>
> ps：用补偿刀收尾会影响补偿判断，如果用补偿刀收尾需要报补偿

[源码](./src/client)

[介绍](https://yobot.win)
