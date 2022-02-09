Cheatsheets for funcx tooling for use with the `cheat` tool

To learn about cheat and see install docs:
    https://github.com/cheat/cheat


To use cheatsheets from this repo, assuming it is found in
/home/userfoo/code/helm-chart/ , add the following to your
~/.config/cheat/conf.yml :

  - name: funcx
    path: /home/userfoo/funcx/helm-chart/cheatsheets
    tags: [ funcx ]
    readonly: false


Try out

    cheat funcx-release
    cheat funcx-microk8s
