def process_admins(idioma):
    f=open('admins_'+idioma+'.txt')
    try:
        lines=f.readlines()
    finally:
        f.close()
    
    linesw=[]    
    linesw.append(r'author_text="')
    num_admins=len(lines)
    for line in lines:
        linesw.append(line.strip(' \n*').rsplit('(',1).pop(0).strip())
        linesw.append(r'" OR author_text="')
    linesw.pop()
    linesw.append('"')
    
    fw=open('admins_processed_'+idioma+'.txt', 'w')
    try:
        fw.writelines(linesw)
    finally:
        fw.close()

    fr=open('admins_processed_'+idioma+'.txt')
    try:
        where_clause=fr.read()
    finally:
        fr.close()
    print where_clause+"\n\n"
    print num_admins
    return [where_clause, num_admins]
    
def process_users_ids(list_users_ids,idioma):
    lines=[]
    lines.append("author='")
    for line in list_users_ids:
        lines.append(str(line))
        lines.append("' OR author='")
    lines.pop()
    lines.append("'")
    f=open('users_ids_'+idioma+'.txt', 'w')
    try:
        f.writelines(linesw)
    finally:
        f.close()
    fr=open('users_ids_'+idioma+'.txt')
    try:
        where_clause=fr.read()
    finally:
        fr.close()
    return where_clause
##process_admins("enwiki")
