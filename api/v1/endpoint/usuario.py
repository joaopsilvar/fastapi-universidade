from typing import List, Optional,AnyStr
from fastapi import APIRouter,status,Depends,HTTPException,Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from models.usuario_model import UsuarioModel
from schemas.usuario_schema import UsuarioSchemaBase,UsuarioSchemaCreate,UsuarioSchemaArtigos,UsuarioSchemaUp
from core.deps import get_current_user,get_session
from core.security import gerar_hash_senha
from core.auth import autenticar,criar_token_acesso

router = APIRouter()

@router.get('/logado', response_model=UsuarioSchemaBase)
def get_logado(usuario_logado:UsuarioModel = Depends(get_current_user)):
    return usuario_logado

@router.post('/singup', response_model=UsuarioSchemaBase, status_code=status.HTTP_201_CREATED)
async def post_usuario(usuario:UsuarioSchemaCreate, db:AsyncSession = Depends(get_session)):
    novo_usuario = UsuarioModel(
        nome=usuario.nome,
        sobrenome=usuario.sobrenome,
        email=usuario.email,
        senha=gerar_hash_senha(usuario.senha),
        eh_admin = usuario.eh_admin
    )
    async with db as session:
        try:
            session.add(novo_usuario)
            await session.commit()
            return novo_usuario
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='Ja existe um usuario com o email cadastrado')
    
@router.get('/',response_model=List[UsuarioSchemaBase], status_code=status.HTTP_200_OK)
async def get_usuarios(db:AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel)
        result = await session.execute(query)
        usuarios:List[UsuarioSchemaBase] = result.scalars().unique().all()

        return usuarios
    
@router.get('/{usuario_id}', response_model=UsuarioSchemaArtigos, status_code=status.HTTP_200_OK)
async def get_usuario(usuario_id:int, db:AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == usuario_id)
        result = await session.execute(query)
        usuario:UsuarioSchemaArtigos = result.scalars().unique().one_or_none()

        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Usuario nao encontrado')
        
        return usuario

@router.put('/{usuario_id}', response_model=UsuarioSchemaBase, status_code=status.HTTP_200_OK)
async def put_usuario(usuario_id:int,usuario:UsuarioSchemaUp ,db:AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == usuario_id)
        result = await session.execute(query)
        usuario_up:UsuarioSchemaUp = result.scalars().unique().one_or_none()

        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Usuario nao encontrado')

        if usuario.nome:
            usuario_up.nome = usuario.nome
        if usuario.sobrenome:
            usuario_up.sobrenome = usuario.sobrenome
        if usuario.email:
            usuario_up.email = usuario.email
        if usuario.eh_admin is not None:
            usuario_up.eh_admin = usuario.eh_admin
        if usuario.senha:
            usuario_up.senha = gerar_hash_senha(usuario.senha)

        await session.commit()
        
        return usuario_up
    
@router.delete('/{usuario_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(usuario_id:int, db:AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == usuario_id)
        result = await session.execute(query)
        usuario_del:UsuarioSchemaArtigos = result.scalars().unique().one_or_none()

        if not usuario_del:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Usuario nao encontrado')
        
        await session.delete(usuario_del)
        await session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
@router.post('/login')
async def login(form_data:OAuth2PasswordRequestForm = Depends(), db:AsyncSession = Depends(get_session)):
    usuario = await autenticar(email=form_data.username, senha=form_data.password,db=db)

    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Dados de acesso incorreto')
    
    return JSONResponse(content={"access_token": criar_token_acesso(sub=usuario.id),"token_type":"bearer"},status_code=status.HTTP_200_OK)